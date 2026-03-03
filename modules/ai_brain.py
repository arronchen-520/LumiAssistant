"""
ai_brain.py — 核心 AI：统一输入处理 · 时间解析 · 聊天路由

关键设计理念 (Unified Input Architecture):
  传统流程: 录音 → 存储日记 | 聊天 → 查询记忆  (两条独立路径)
  新流程:   录音 → 单次 LLM 调用同时判断意图
              → 如果是日记: 反思 + 提醒 + 标签
              → 如果是记忆查询: 查询 SQLite + 生成回答
              → 如果两者兼有: 全部处理，一次性回复
  结果: 用户说"我今天很累，顺便我上周都做了什么？" → 存储情绪 + 回答记忆查询
"""
import json
import re
from collections import deque
from datetime import datetime

from modules.llm_client import chat

# ── 会话历史 (Conversation History) ──────────────────────────────────────────

MAX_HISTORY = 20
_history: deque[dict] = deque(maxlen=MAX_HISTORY)


def clear_history():
    _history.clear()


# ── 统一输入处理系统提示 (Unified Input Processing) ───────────────────────────

_UNIFIED_SYSTEM = """\
You are 灵犀, the user's personal AI diary companion (LumiLog · 灵犀笔记).
Current time: {now}.

The user has sent text (typed or transcribed from voice). Your job is to:
1. Determine the INTENT. Is this a diary entry, a memory query, a casual chat, a brainstorm request, a command, or a persona update?
2. Process accordingly and return ONLY valid JSON:

{{
  "input_type": "diary" | "query" | "both" | "chit-chat" | "brainstorm" | "command" | "persona_update",
  "reflection": "2-3 warm sentences (for diary, both, or chit-chat, else null)",
  "reminders":  [{{"message": "...", "time_description": "exact phrase"}}],
  "summary_tags": ["tag1", "tag2"],
  "memory_query": "the question extracted for memory retrieval (if query or both, else null)",
  "brainstorm_topic": "the extracted topic to brainstorm/advise on (if brainstorm, else null)",
  "command_action": "delete_last" | null (if command),
  "persona_updates": [{{"key": "...", "value": "..."}}] (if persona_update)
}}

Classification rules:
- "diary"   : sharing feelings, events, thoughts, plans
- "query"   : asking about past entries, schedule, or what they did
- "both"    : diary content AND asking about the past
- "chit-chat": casual greetings, casual praise without substance (e.g. "Good morning", "You are cute")
- "brainstorm": asking for detailed advice, planning, or brainstorming (e.g. "I'm nervous about my interview tomorrow, any tips?", "Help me plan a trip")
- "command" : app-level commands like "Delete my last diary entry"
- "persona_update": user mentioning long-term preferences, name, or goals for you to remember (e.g. "Call me Alex", "I am trying to diet, supervise me")

Reflection rules (diary/both/chit-chat):
- Reply in the SAME language as the user
- Be warm and specific. Empathise.
- For chit-chat, just give a warm quick reply.

brainstorm_topic rules:
- Extract the core topic the user wants advice on.

persona_updates rules:
- Extract simple key-value pairs representing the user's profile/preferences to remember long-term.
- E.g. {{"key": "user_name", "value": "Alex"}}, {{"key": "current_goal", "value": "eat less carbs"}}

User Persona / Long-term Memory for context:
{persona}\
"""


def process_input(text: str, context_entries: list = None) -> dict:
    from modules.memory import answer_memory_query
    from modules.database import get_all_personas

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Load persona context
    personas = get_all_personas()
    persona_str = "\n".join(f"- {k}: {v}" for k, v in personas.items()) if personas else "None yet."

    # Build recent diary context for the unified prompt
    context = ""
    if context_entries:
        context = "\nRecent diary context:\n"
        for e in context_entries[:5]:
            context += f"  [{e['date']}] {e['text'][:200]}\n"

    raw = chat(
        _UNIFIED_SYSTEM.format(now=now, persona=persona_str),
        f"{context}\nUser input:\n{text}",
        temperature=0.3,
    )
    raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
    m   = re.search(r'\{.*\}', raw, re.DOTALL)
    if m:
        raw = m.group(0)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "input_type":   "diary",
            "reflection":   raw[:300] or "谢谢你今天的分享 ✨",
            "reminders":    [],
            "summary_tags": [],
            "memory_query": None,
        }

    input_type = result.get("input_type", "diary")

    # ── Handle Brainstorm / Copilot Request ────────────────────────────────
    if input_type == "brainstorm":
        topic = result.get("brainstorm_topic") or text
        sys_prompt = (
            f"You are 灵犀, a helpful AI companion. The user wants to brainstorm or needs advice on: {topic}.\n"
            f"Provide a thoughtful, structured, and helpful response. Be encouraging and practical.\n"
            f"User Persona info:\n{persona_str}"
        )
        advice = chat(sys_prompt, text, temperature=0.7)
        # Put the long response in query_answer so it shows up beautifully in the UI
        result["query_answer"] = advice
        result["reflection"] = "💡 我为你整理了一些想法，希望能帮到你！"
        return result

    # ── 如果包含记忆查询，执行检索 ──────────────────────────────────────────
    query_answer = None
    memory_q = result.get("memory_query")
    if memory_q and input_type in ("query", "both"):
        try:
            query_answer = answer_memory_query(memory_q, context_entries)
        except Exception as e:
            query_answer = f"抱歉，记忆查询出了点问题 🌙 ({e})"
        result["query_answer"] = query_answer

    return result


# ── 时间解析 (Time Parsing: dateparser-first, LLM fallback) ──────────────────

def parse_reminder_time(description: str) -> datetime | None:
    # 1. dateparser 快速解析
    try:
        import dateparser
        dt = dateparser.parse(
            description,
            settings={"PREFER_DATES_FROM": "future", "RETURN_AS_TIMEZONE_AWARE": False},
        )
        if dt:
            return dt
    except ImportError:
        pass

    # 2. LLM 兜底
    _TIME_SYSTEM = (
        "Current time: {now}. "
        "Convert the user's time description to ISO 8601: YYYY-MM-DDTHH:MM:SS. "
        "Return ONLY the datetime string. If ambiguous, return: null"
    )
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    raw = chat(_TIME_SYSTEM.format(now=now_str), description, temperature=0.0)
    raw = raw.strip().strip('"\'')
    if not raw or raw.lower() == "null":
        return None
    try:
        return datetime.fromisoformat(raw[:19])
    except ValueError:
        return None


# ── 聊天路由 (Chat Routing — Chat Tab) ───────────────────────────────────────
# 聊天标签页仍保留独立会话历史，适合纯对话场景。

_CHAT_SYSTEM = """\
You are 灵犀, a warm desktop diary pet companion (LumiLog · 灵犀笔记).
Personality: warm, gentle, occasionally playful — like a close friend who knows them well.
Rules:
  - Reply in the SAME language as the user (Chinese or English)
  - Keep it concise: 1-3 sentences
  - Use emoji naturally, not excessively
  - You have memory of this conversation — refer back to what was said when relevant
{context}\
"""


def chat_with_pet(user_message: str, recent_entries: list = None) -> str:
    """聊天标签页的对话入口，维护独立会话历史。"""
    from modules.memory import is_memory_query, answer_memory_query

    if is_memory_query(user_message):
        answer = answer_memory_query(user_message, recent_entries)
        if answer is not None:
            _history.append({"role": "user",      "content": user_message})
            _history.append({"role": "assistant",  "content": answer})
            return answer

    context = ""
    if recent_entries:
        context = "Recent diary snippets (use for context, don't mention unless relevant):\n"
        for e in recent_entries[:8]:
            context += f"  [{e['date']}] {e['text'][:150]}\n"

    history_snapshot = list(_history)
    reply = chat(
        _CHAT_SYSTEM.format(context=context),
        user_message,
        temperature=0.8,
        history=history_snapshot,
    )

    _history.append({"role": "user",      "content": user_message})
    _history.append({"role": "assistant", "content": reply})
    return reply

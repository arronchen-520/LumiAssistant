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
1. Determine the INTENT: is this a diary entry, a memory query, or both?
2. Process accordingly and return ONLY valid JSON:

{{
  "input_type": "diary" | "query" | "both",
  "reflection": "2-3 warm, specific sentences (if diary or both, else null)",
  "reminders":  [{{"message": "...", "time_description": "exact phrase from text"}}],
  "summary_tags": ["tag1", "tag2"],
  "memory_query": "the question extracted for memory retrieval (if query or both, else null)"
}}

Classification rules:
- "diary"  → user is sharing feelings, events, thoughts, plans, or what happened
- "query"  → user is asking about past entries, schedule, reminders, or what they did
- "both"   → text contains diary content AND asks about the past
             e.g. "I'm exhausted. What did I do last week?" → both

Reflection rules (if applicable):
- Reply in the SAME language as the user (Chinese or English)
- Be warm and specific — reference what they actually said
- 2-3 sentences, with emoji used naturally not excessively

Reminder rules:
- Extract ONLY explicit, time-anchored todos the user mentioned

memory_query rules:
- If the user is asking about their diary, extract the question verbatim or cleaned up
- e.g. "顺便我上周都做了啥" → "我上周做了什么？"\
"""


def process_input(text: str, context_entries: list = None) -> dict:
    """
    统一入口：对用户输入做意图分类 + 日记分析 + 记忆查询（如需要）。

    Returns:
        {
            "input_type":    "diary" | "query" | "both",
            "reflection":    str | None,     # diary 反思
            "query_answer":  str | None,     # memory 查询回答
            "reminders":     list,
            "summary_tags":  list,
        }
    """
    from modules.memory import answer_memory_query

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build recent diary context for the unified prompt
    context = ""
    if context_entries:
        context = "\nRecent diary context:\n"
        for e in context_entries[:5]:
            context += f"  [{e['date']}] {e['text'][:200]}\n"

    raw = chat(
        _UNIFIED_SYSTEM.format(now=now),
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
        # 解析失败 → 降级为纯日记反思
        result = {
            "input_type":   "diary",
            "reflection":   raw[:300] or "谢谢你今天的分享 ✨",
            "reminders":    [],
            "summary_tags": [],
            "memory_query": None,
        }

    # ── 如果包含记忆查询，执行检索 ──────────────────────────────────────────
    query_answer = None
    memory_q = result.get("memory_query")
    if memory_q:
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

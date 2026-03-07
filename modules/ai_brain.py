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
You are Lumi, the user's personal AI diary companion (LumiAssistant).
Current time: {now}.

The user has sent text (typed or transcribed from voice). Your job is to:
1. Determine the INTENT. Is this a diary entry, a memory query, a casual chat, a brainstorm request, a command, or a persona update?
2. CRITICAL: The input text might be transcribed by an STT (Speech-to-Text) engine. It may contain homophones, lack punctuation, or have weird typos (e.g. 'rest run' instead of 'restaurant' / '我今天吃了考家' instead of '烤鸭'). You MUST infer the true intended meaning contextually.
3. Process accordingly and return ONLY valid JSON:

{{
  "input_type": "diary" | "query" | "both" | "chit-chat" | "brainstorm" | "command" | "persona_update" | "todo",
  "diary_date": "YYYY-MM-DD or null (ONLY if the user explicitly specifies a past/future date for THIS diary entry, e.g. 'yesterday')",
  "reflection": "2-3 warm sentences (for diary, both, chit-chat, or todo, else null)",
  "summary_tags": ["tag1", "tag2"],
  "memory_query": "the question extracted for memory retrieval (if query or both, else null)",
  "brainstorm_topic": "the extracted topic to brainstorm/advise on (if brainstorm, else null)",
  "command_list": [
     {{
         "action": "delete_last_entry" | "delete_entry_by_date" | "update_entry_by_date" | "complete_todo" | "update_todo" | "delete_todo",
         "target_date": "YYYY-MM-DD or null",
         "target_keyword": "keyword to find the todo or null",
         "new_text": "new text content or null",
         "new_time": "YYYY-MM-DD HH:MM or null",
         "new_status": "pending | in_progress | done (for todo commands, else null)",
         "notes": "progress notes for todo update or null"
     }}
  ] (if command, else null),
  "persona_updates": [{{"key": "...", "value": "..."}}] (if persona_update),
  "todo_actions": [
     {{
         "action": "add_todo" | "update_todo" | "complete_todo" | "delete_todo",
         "task": "task description",
         "project": "project/category name or null",
         "notes": "progress notes or null",
         "target_keyword": "keyword to find existing todo item",
         "priority": "high | medium | low",
         "deadline": "YYYY-MM-DD or null"
     }}
  ] (if todo, else null)
}}

Classification rules:
- "diary"   : sharing feelings, events, thoughts, plans
- "query"   : asking about past entries, schedule, or what they did
- "both"    : diary content AND asking about the past
- "chit-chat": casual greetings, casual praise without substance (e.g. "Good morning", "You are cute")
- "brainstorm": asking for detailed advice, planning, or brainstorming (e.g. "I'm nervous about my interview tomorrow, any tips?")
- "command" : app-level commands like "Delete my last diary entry" or "Delete yesterday's diary" or "Delete that todo" or "Mark TODO as complete"
- "persona_update": user mentioning long-term preferences, name, or goals for you to remember (e.g. "Call me Alex", "I am trying to diet, supervise me")
- "todo": user mentions adding a to-do item, reporting project progress, or updating task status (e.g. "I need to finish writing chapter 3", "The report is done, next I need to do the presentation", "项目A做到第二步了，下一步是测试")

Reflection rules (diary/both/chit-chat):
- Reply in the SAME language as the user
- Be warm and specific. Empathise.
- For chit-chat, just give a warm quick reply.

brainstorm_topic rules:
- Extract the core topic the user wants advice on.

persona_updates rules:
- Extract simple key-value pairs representing the user's profile/preferences to remember long-term.
- E.g. {{"key": "user_name", "value": "Alex"}}, {{"key": "current_goal", "value": "eat less carbs"}}

todo_actions rules:
- When the user talks about work progress, project tasks, or things they need to do, classify as "todo".
- For new tasks: action="add_todo", fill task and optionally project.
- When user says "X is done" or "finished X": action="complete_todo", set target_keyword to identify the existing todo.
- When user reports progress ("X is at step 2, next is step 3"): action="update_todo", set target_keyword, notes for progress, and optionally add a new add_todo for the next step.
- You can return MULTIPLE todo_actions in one response (e.g. complete one + add another).
- Infer priority from urgency cues: "urgent"/"紧急"/"赶紧" → high, "有空再"→ low, default → medium.
- Infer deadline from time cues: "by Friday" / "周五前" / "下周" → YYYY-MM-DD.
- For big tasks, consider suggesting subtask breakdown in the reflection.
- Always give a warm, encouraging reflection when processing todo updates.

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
        for e in context_entries:
            context += f"  [{e['date']}] {e['text']}\n"

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
            "summary_tags": [],
            "memory_query": None,
        }

    input_type = result.get("input_type", "diary")

    # ── Handle Brainstorm / Copilot Request ────────────────────────────────
    if input_type == "brainstorm":
        topic = result.get("brainstorm_topic") or text
        sys_prompt = (
            f"You are Lumi, a helpful AI companion. The user wants to brainstorm or needs advice on: {topic}.\n"
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




# ── 聊天路由 (Chat Routing — Chat Tab) ───────────────────────────────────────
# 聊天标签页仍保留独立会话历史，适合纯对话场景。

_CHAT_SYSTEM = """\
You are Lumi, a warm desktop diary pet companion (LumiAssistant).
Personality: warm, gentle, occasionally playful — like a close friend who knows them well.
Rules:
  - Reply in the SAME language as the user (Chinese or English)
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
            context += f"  [{e['date']}] {e['text']}\n"

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

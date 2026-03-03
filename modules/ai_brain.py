"""
ai_brain.py - Core AI: diary analysis, time parsing, chat routing.
All LLM calls go through llm_client (OpenAI SDK → local Ollama).

Key improvements over v1:
  - Persistent conversation history (rolling 20 turns) for stateful chat
  - dateparser replaces LLM-based reminder time parsing (instant, no API call)
  - Richer context window: more entries, more characters passed to LLM
  - Rebranded to 灵犀 (LumiLog)
"""
import json
import re
from collections import deque
from datetime import datetime

from modules.llm_client import chat

# ── Conversation History ───────────────────────────────────────────────────────

MAX_HISTORY = 20  # keep last N turns (user + assistant alternating)

# Rolling deque of {"role": "user"|"assistant", "content": "..."}
_history: deque[dict] = deque(maxlen=MAX_HISTORY)


def clear_history():
    """Reset conversation history (e.g., on app restart or explicit user request)."""
    _history.clear()


# ── Diary Analysis ────────────────────────────────────────────────────────────

_ANALYZE_SYSTEM = """\
You are 灵犀, a warm AI diary companion (LumiLog · 灵犀笔记).
Analyze the diary entry and return ONLY valid JSON — no markdown fences, no extra text:
{
  "reflection":   "2-3 warm, insightful sentences in the same language as the diary",
  "reminders":    [{"message": "...", "time_description": "exact phrase from text"}],
  "summary_tags": ["tag1", "tag2"]
}
- reminders: extract ONLY explicit, time-anchored todos the user mentioned
- summary_tags: 2-4 short topic keywords in the diary's language\
"""


def analyze_entry(text: str, context_entries: list = None) -> dict:
    context = ""
    if context_entries:
        # Increased: 5 entries (was 3), 200 chars (was 80)
        context = "Recent diary context (for continuity):\n"
        for e in context_entries[:5]:
            context += f"  [{e['date']}] {e['text'][:200]}\n"
        context += "\n"

    raw = chat(_ANALYZE_SYSTEM, f"{context}Today's entry:\n{text}", temperature=0.4)
    raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
    m   = re.search(r'\{.*\}', raw, re.DOTALL)
    if m:
        raw = m.group(0)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"reflection": raw[:300] or "Thanks for sharing today ✨",
                "reminders": [], "summary_tags": []}


# ── Natural Language Time Parsing (dateparser-first, LLM fallback) ────────────

def parse_reminder_time(description: str) -> datetime | None:
    """
    Parse a natural language time description into a datetime.

    Strategy:
      1. Try dateparser (instant, free, handles zh/en/mixed)
      2. Fall back to LLM if dateparser returns None
    """
    # 1. dateparser — fast path
    try:
        import dateparser
        dt = dateparser.parse(
            description,
            settings={
                "PREFER_DATES_FROM": "future",
                "RETURN_AS_TIMEZONE_AWARE": False,
                "TO_TIMEZONE": "UTC",
            }
        )
        if dt:
            return dt
    except ImportError:
        pass  # dateparser not installed → fall through to LLM

    # 2. LLM fallback
    _TIME_SYSTEM = (
        "Current time: {now}. "
        "Convert the user's time description to ISO 8601 format: YYYY-MM-DDTHH:MM:SS. "
        "Return ONLY the datetime string. If ambiguous or unparseable, return: null"
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


# ── Chat with Memory Routing + Conversation History ───────────────────────────

_CHAT_SYSTEM = """\
You are 灵犀, the user's desktop diary pet companion (LumiLog · 灵犀笔记).
Personality: warm, gentle, occasionally playful — like a close friend who knows them well.
Rules:
  - Reply in the same language as the user (Chinese or English)
  - Keep it concise: 1-3 sentences
  - Use emoji naturally, not excessively
  - You have memory of this conversation — refer back to what was said when relevant
{context}\
"""


def chat_with_pet(user_message: str, recent_entries: list = None) -> str:
    """
    Route to memory pipeline or casual chat.
    Maintains rolling conversation history across calls for stateful dialogue.
    """
    from modules.memory import is_memory_query, answer_memory_query

    # Memory queries bypass conversation history (they have their own context)
    if is_memory_query(user_message):
        answer = answer_memory_query(user_message, recent_entries)
        if answer is not None:
            # Still record the exchange in history so follow-ups work
            _history.append({"role": "user",      "content": user_message})
            _history.append({"role": "assistant",  "content": answer})
            return answer
        # Planner decided it's general_chat → fall through

    # Build diary context snippet (increased: 8 entries, 150 chars each — was 3×60)
    context = ""
    if recent_entries:
        context = "Recent diary snippets (use for context, don't mention unless relevant):\n"
        for e in recent_entries[:8]:
            context += f"  [{e['date']}] {e['text'][:150]}\n"

    # Grab current history *before* appending the new message
    history_snapshot = list(_history)

    # Generate reply with full history
    reply = chat(
        _CHAT_SYSTEM.format(context=context),
        user_message,
        temperature=0.8,
        history=history_snapshot,
    )

    # Record this turn
    _history.append({"role": "user",      "content": user_message})
    _history.append({"role": "assistant", "content": reply})

    return reply

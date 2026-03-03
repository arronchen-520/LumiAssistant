"""
ai_brain.py - Core AI: diary analysis, time parsing, chat routing.
All LLM calls go through llm_client (OpenAI SDK → local Ollama).
"""
import json
import re
from datetime import datetime

from modules.llm_client import chat

# ── Diary Analysis ────────────────────────────────────────────────────────────

_ANALYZE_SYSTEM = """\
You are 小记, a warm AI diary companion.
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
        context = "Recent diary context (for continuity):\n"
        for e in context_entries[:3]:
            context += f"  [{e['date']}] {e['text'][:80]}\n"
        context += "\n"

    raw = chat(_ANALYZE_SYSTEM, f"{context}Today's entry:\n{text}", temperature=0.4)
    raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
    m   = re.search(r'\{.*\}', raw, re.DOTALL)
    if m:
        raw = m.group(0)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Graceful fallback: use whatever text came back as the reflection
        return {"reflection": raw[:300] or "Thanks for sharing today ✨",
                "reminders": [], "summary_tags": []}


# ── Natural Language Time Parsing ─────────────────────────────────────────────

_TIME_SYSTEM = (
    "Current time: {now}. "
    "Convert the user's time description to ISO 8601 format: YYYY-MM-DDTHH:MM:SS. "
    "Return ONLY the datetime string. If the description is ambiguous or unparseable, return: null"
)


def parse_reminder_time(description: str) -> datetime | None:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    raw = chat(_TIME_SYSTEM.format(now=now_str), description, temperature=0.0)
    raw = raw.strip().strip('"\'')
    if not raw or raw.lower() == "null":
        return None
    try:
        return datetime.fromisoformat(raw[:19])
    except ValueError:
        return None


# ── Chat with Memory Routing ──────────────────────────────────────────────────

_CHAT_SYSTEM = """\
You are 小记, the user's desktop diary pet companion.
Personality: warm, gentle, occasionally playful — like a close friend who knows them well.
Rules:
  - Reply in the same language as the user (Chinese or English)
  - Keep it concise: 1-3 sentences
  - Use emoji naturally, not excessively
{context}\
"""


def chat_with_pet(user_message: str, recent_entries: list = None) -> str:
    """Route to memory pipeline or casual chat based on message content."""
    from modules.memory import is_memory_query, answer_memory_query

    if is_memory_query(user_message):
        answer = answer_memory_query(user_message, recent_entries)
        if answer is not None:
            return answer
        # Planner decided it's general_chat → fall through

    context = ""
    if recent_entries:
        context = "Recent diary snippets (use for context, don't mention unless relevant):\n"
        for e in recent_entries[:3]:
            context += f"  [{e['date']}] {e['text'][:60]}\n"

    return chat(_CHAT_SYSTEM.format(context=context), user_message, temperature=0.8)

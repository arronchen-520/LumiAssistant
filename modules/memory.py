import json
import re
from datetime import datetime, timedelta

from modules.llm_client import chat
from modules.database import (
    get_entries_by_date,
    get_entries_by_keywords,
    get_upcoming_reminders_window,
    get_reminders_by_date,
)

# ── Query Planner ─────────────────────────────────────────────────────────────

_PLANNER_SYSTEM = """\
You are a query planner for a personal diary app (LumiLog · 灵犀笔记). Current datetime: {now}.

Analyze the user's message and output ONLY valid JSON — no markdown, no explanation:
{{
  "query_type": "date_range" | "keyword" | "tasks" | "general_chat",
  "date_start": "YYYY-MM-DD or null",
  "date_end":   "YYYY-MM-DD or null",
  "keywords":   ["word1", "word2"],
  "summary_mode": true | false
}}

query_type rules:
  "date_range"   — user mentions a specific time period
                   (yesterday, today, last week, last month, this week, this month,
                    昨天, 今天, 上周, 上个月, 本周, 本月, 3 days ago, March 15)
  "keyword"      — user asks about a topic with no clear date
                   (gym, stress, work, project, meeting, 健身, 压力, 工作, 项目)
  "tasks"        — user asks about upcoming schedule/reminders/todos
                   (next week, tomorrow, what do I have, what's coming up,
                    下周, 明天, 接下来, 有什么安排, 待办)
  "general_chat" — everything else (greetings, advice, opinions, how-are-you)

Other rules:
  - Compute exact YYYY-MM-DD dates relative to the current datetime above
  - For "昨天" / "yesterday" → date_start = date_end = yesterday's date
  - For "上周" / "last week"  → date_start = Monday, date_end = Sunday of last week
  - For "本周" / "this week"  → date_start = this Monday, date_end = today
  - summary_mode = true when user wants an overview; false when searching for something specific
  - keywords: extract in original language
  - If unsure, prefer "date_range" or "keyword" over "general_chat"\
"""


def _plan_query(question: str) -> dict:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    raw = chat(_PLANNER_SYSTEM.format(now=now), question, temperature=0.0)

    raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
    m   = re.search(r'\{.*\}', raw, re.DOTALL)
    raw = m.group(0) if m else raw

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"query_type": "general_chat", "date_start": None,
                "date_end": None, "keywords": [], "summary_mode": False}


# ── Retrieval ─────────────────────────────────────────────────────────────────

def _retrieve(plan: dict) -> dict:
    qtype    = plan.get("query_type", "general_chat")
    start    = plan.get("date_start")
    end      = plan.get("date_end")
    keywords = plan.get("keywords") or []
    entries, tasks = [], []

    if qtype == "date_range" and start:
        entries = get_entries_by_date(start, end or start)
        if not entries and keywords:          # fallback to keyword if date yields nothing
            entries = get_entries_by_keywords(keywords)

    elif qtype == "keyword":
        entries = get_entries_by_keywords(keywords)
        if not entries and start:             # fallback to date
            entries = get_entries_by_date(start, end or start)

    elif qtype == "tasks":
        if start:
            tasks = get_reminders_by_date(start, end or start)
            entries = get_entries_by_date(start, end or start)
        else:
            tasks = get_upcoming_reminders_window(days=30)

    # Deduplicate entries (can appear from both date + keyword paths)
    seen, unique = set(), []
    for e in entries:
        if e["id"] not in seen:
            seen.add(e["id"])
            unique.append(e)

    return {"entries": unique, "tasks": tasks}


# ── Answer Generator ──────────────────────────────────────────────────────────

_ANSWER_SYSTEM = """\
You are Lumi, a warm and caring AI diary companion (LumiLog · 灵犀笔记). Current time: {now}.
The user asked about their diary memories or upcoming schedule.
You have been given the retrieved diary entries and reminders below.

Instructions:
- The user's question may be transcribed from voice (STT) and contain homophone typos. Infer the correct meaning contextually.
- Answer in the same language as the user's question (Chinese or English)
- Be warm, specific, and reference actual content from the entries
- For summaries, highlight the most interesting/important moments
- If no relevant entries were found, say so gently and encourage them to write more
- Keep it conversational — 2–5 sentences for simple queries, more for full summaries\
"""


def _generate_answer(question: str, retrieved: dict) -> str:
    entries = retrieved["entries"]
    tasks   = retrieved["tasks"]
    now     = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines: list[str] = []
    if entries:
        lines.append("=== Diary Entries ===")
        for e in entries:
            lines.append(f"[{e['date']}] {e['text']}")
            if e["reflection"]:
                lines.append(f"  AI note: {e['reflection']}")

    if tasks:
        lines.append("\n=== Upcoming Reminders ===")
        for t in tasks:
            lines.append(f"[{t['time']}] {t['message']}")

    if not lines:
        lines = ["=== No matching diary entries found ==="]

    context = "\n".join(lines)
    return chat(
        _ANSWER_SYSTEM.format(now=now),
        f"Retrieved data:\n{context}\n\nUser's question: {question}",
        temperature=0.7,
    )


# ── Public interface ──────────────────────────────────────────────────────────

# Cheap keyword pre-filter — avoids calling the planner for obvious casual chat.
_MEMORY_HINTS = {
    # Chinese
    "昨天", "前天", "今天", "上周", "本周", "上个月", "本月", "那天", "之前", "记得",
    "做了什么", "发生了什么", "下周", "明天", "任务", "提醒", "安排", "计划", "待办",
    "什么时候", "有没有", "日记", "记录", "找找", "几天前", "有什么", "接下来",
    # English
    "yesterday", "today", "last week", "this week", "last month", "this month",
    "last year", "remind", "schedule", "what did i", "what have i", "when did",
    "diary", "journal", "tomorrow", "next week", "what's coming", "what do i have",
    "tell me about", "when was", "what was",
}


def is_memory_query(message: str) -> bool:
    """Return True if the message looks like a memory/task query."""
    lower = message.lower()
    return any(hint in lower for hint in _MEMORY_HINTS)


def answer_memory_query(question: str, recent_entries: list = None) -> str | None:
    """
    Full memory pipeline.
    Returns answer string, or None if the planner classifies this as general_chat.
    """
    try:
        plan = _plan_query(question)
        print(f"[Memory] plan={plan}")

        if plan.get("query_type") == "general_chat":
            return None

        retrieved = _retrieve(plan)
        print(f"[Memory] {len(retrieved['entries'])} entries, {len(retrieved['tasks'])} tasks")

        return _generate_answer(question, retrieved)

    except Exception as e:
        msg = str(e)
        if "ollama" in msg.lower() or "connection" in msg.lower():
            return "⚠️ Can't reach Ollama — is it running? (`ollama serve`)"
        print(f"[Memory] unexpected error: {e}")
        return "Sorry, I had trouble searching your memories just now 🌙"

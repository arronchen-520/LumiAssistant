<div align="center">

<img src="https://img.shields.io/badge/LumiLog-灵犀笔记-a78bfa?style=for-the-badge&labelColor=0d0d1a" alt="LumiLog"/>

# ✦ LumiLog · 灵犀笔记

**Your AI companion that lives on your desktop, listens to your day, and actually remembers.**

*Speak → Reflect → Remember → Ask anything*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3b82f6?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20%28local%29-a78bfa?style=flat-square)](https://ollama.com)
[![Groq](https://img.shields.io/badge/STT-Groq%20Whisper-34d399?style=flat-square)](https://console.groq.com)
[![SQLite](https://img.shields.io/badge/Storage-SQLite%20+%20FTS5-f59e0b?style=flat-square)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-64748b?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourname/lumilog?style=flat-square&color=fde68a)](https://github.com/yourname/lumilog/stargazers)

<br/>

> *"Your diary should know you — not just store you."*

</div>

---

LumiLog is a **floating desktop pet + AI diary** that sits quietly in the corner of your screen. Tap to open. Speak your day. It transcribes in ~1 second, reflects back something real, extracts your reminders, and builds a memory of you — one entry at a time.

Then ask it anything:

```
You:    "What was I stressed about last week?"
灵犀:   "You had three back-to-back deadlines and mentioned feeling
         behind on the project twice. You also wrote that you were
         proud of finally finishing the design doc on Thursday. ✦"

You:    "Summarise that more briefly."
灵犀:   "Stressful week, but ended with a win. ✓"
```

**Everything runs on your machine. Your diary never leaves.**

---

## Why LumiLog?

| | LumiLog | Notion / Apple Notes | Day One |
|---|---|---|--|
| Voice → text in ~1s | ✅ Groq Whisper | ❌ | 💰 premium |
| AI that *reads* your entries | ✅ local Ollama | ❌ | ❌ |
| Remembers what you said last week | ✅ memory pipeline | ❌ | ❌ |
| Conversation history across questions | ✅ 20-turn context | ❌ | ❌ |
| 100% private, runs offline | ✅ | ❌ cloud | ❌ cloud |
| Cute pet on your desktop | ✅ obviously | 😐 | 😐 |

---

## Features

### 🐾 Desktop Pet
A floating animated companion that lives in the corner of your screen. Drag it anywhere. It breathes, blinks, bounces when happy, and drifts to sleep if you've been away too long.

```
idle  →  breathing sway, random blinks
listening  →  dots pulse above head
happy  →  sparkles, upward-curve smile, bounce
sleepy  →  Zzz bubbles after 10 min idle
```

### 🎙️ Voice-First, ~1 Second Transcription
Hit record, talk naturally — in Chinese, English, or both. [Groq Whisper](https://console.groq.com) handles it in about one second. The transcript lands in the box, ready to save. No language selection needed — it auto-detects.

### 💭 Grounded AI Reflection
After saving, your local Ollama model reads what you wrote and responds with a short, *specific* reflection. Not "sounds tough!" — but "you've mentioned the same project slipping three times this week."

### 🧠 Conversation Memory
Ask questions like a normal person. LumiLog maintains a full conversation thread — follow-up questions, clarifications, and summaries all work:

```
"What did I do last week?"         → date-range query across diary
"When did I last mention the gym?" → full-text search (FTS5)
"What's coming up this month?"     → reminder lookup
"Summarise that more briefly."     → follow-up, uses prior context ✓
"What was I worried about?"        → keyword semantic routing
```

### ⏰ Smart Reminders — Extracted Automatically
Just write naturally. LumiLog parses the time and sets the reminder:

```
"Remind me to follow up with Sarah on Friday at 3pm"
"Meeting with Tom tomorrow at 10"
"Call the dentist next Monday morning"
```

A popup fires when the moment arrives — no calendar app needed.

### 💬 Stateful Chat
The chat tab maintains a rolling 20-turn conversation history. 灵犀 knows what it said three messages ago, and can refer back to it.

---

## Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | [Ollama](https://ollama.com) (local) | Fully private. No API cost. Swap any model. |
| STT | [Groq Whisper](https://console.groq.com) | ~10× faster than OpenAI Whisper. Free tier. |
| SDK | `openai` Python package | Both Ollama and Groq expose OpenAI-compatible APIs — one client for everything. |
| DB | SQLite + FTS5 | Zero config. Indexed full-text search. Your data in one portable file. |
| GUI | `tkinter` + Canvas | Ships with Python. Sprite drawn with geometry — no image files. |
| Time parsing | `dateparser` | Parses natural-language times instantly, no LLM round-trip. |

---

## Getting Started

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running locally
- A free [Groq API key](https://console.groq.com) (for Whisper transcription)

### Install

```bash
git clone https://github.com/yourname/lumilog
cd lumilog

pip install -r requirements.txt
```

### Configure

```bash
cp env.example .env
```

Edit `.env`:
```env
GROQ_API_KEY=your_key_here   # from console.groq.com (free)
OLLAMA_MODEL=llama3.2        # or mistral, qwen2.5, gemma3 …
STT_LANGUAGE=                # leave blank for auto-detect (recommended)
```

### Pull a model and start Ollama

```bash
ollama pull llama3.2
ollama serve          # keep this running
```

### Run

```bash
python main.py
```

The pet appears in the **bottom-right corner** of your screen. Click it to open the diary panel.

---

## How to Use

| Action | What happens |
|--------|-------------|
| **Click** the pet | Opens / closes the diary panel |
| **Right-click** | Quick menu: record, set mood, quit |
| **Drag** | Move it anywhere on your screen |
| **🎙️ Record** | Click to start, click to stop + transcribe |
| **Save & Reflect** | Saves entry, triggers AI reflection, extracts reminders |
| **Chat tab** | Ask anything — memory queries or casual conversation |

### Memory queries that work

```
"What did I do yesterday?"
"Summarise last week for me"
"What was I stressed about?"
"When did I last write about work?"
"What do I have coming up next week?"
"Did I write anything about the gym?"
```

### Setting reminders naturally

```
"Meeting with Tom tomorrow at 10am"
"Remember to submit the report by Friday"
"Call dentist next Monday morning"
```

---

## Project Structure

```
lumilog/
├── main.py                        Entry point — wires all callbacks
├── .env.example
├── requirements.txt
├── data/
│   └── diary.db                   SQLite + FTS5 (auto-created)
└── modules/
    ├── llm_client.py              Singleton OpenAI-SDK client → Ollama
    ├── ai_brain.py                Diary analysis · time parsing · chat routing
    │                              └─ 20-turn conversation history
    ├── memory.py                  3-stage memory pipeline (plan → retrieve → answer)
    ├── database.py                SQLite CRUD + FTS5 full-text search
    ├── voice.py                   Microphone capture + Groq Whisper transcription
    ├── reminder_scheduler.py      Background thread firing due reminders
    └── pet_window.py              Desktop pet sprite + full panel UI
```

### Memory pipeline

```
"What did I do last week?"
        │
        ▼
  is_memory_query()          — keyword pre-filter (no LLM, instant)
        │ yes
        ▼
  _plan_query()              — Ollama temp=0: intent → structured JSON
  { "query_type": "date_range",
    "date_start": "2026-02-24",
    "date_end":   "2026-03-02" }
        │
        ▼
  _retrieve()                — FTS5 / date / reminder SQL query
        │
        ▼
  _generate_answer()         — Ollama temp=0.7: synthesise warm reply
        │
        ▼
  "Last week you had three work meetings and were worried about…"
        │
        ▼
  _history.append([user, assistant])   — available for follow-up questions
```

---

## Privacy

All diary data is in `data/diary.db` on your local machine. LLM inference runs entirely through Ollama — **no diary content is ever sent to a cloud API**.

The only external call: Groq Whisper receives your raw audio for transcription. No text, no diary content.

---

## Roadmap

- [ ] Semantic / vector memory (embeddings → cosine search for "that stressful period")
- [ ] VAD auto-stop (silence detection — no more manual stop button)
- [ ] Groq LLM option (removes Ollama requirement for new users)
- [ ] Mood tracking column + weekly mood chart
- [ ] Weekly AI summary reports
- [ ] Export diary as Markdown or PDF
- [ ] Custom pet skins / Live2D integration
- [ ] Cloud sync via Supabase (opt-in)

---

## Contributing

Issues and PRs welcome. If you build something with it, open a discussion — would love to see what people make.

---

<div align="center">
<sub>Built with Python, Ollama, and the belief that your diary should stay yours.</sub>
<br/>
<sub>✦ Star if you like it — it helps more people find this ✦</sub>
</div>

<div align="center">

<img src="https://img.shields.io/badge/LumiLog-灵犀笔记-a78bfa?style=for-the-badge&labelColor=0d0d1a" alt="LumiLog"/>

# ✦ LumiLog · 灵犀笔记

**Your AI companion that lives on your desktop, hears your day, and actually remembers.**

*Speak → Reflect → Remember → Ask anything — in one flow.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3b82f6?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20%2F%20Groq%20%2F%20OpenAI-a78bfa?style=flat-square)](https://ollama.com)
[![Groq](https://img.shields.io/badge/STT-Groq%20Whisper-34d399?style=flat-square)](https://console.groq.com)
[![SQLite](https://img.shields.io/badge/Storage-SQLite%20+%20FTS5-f59e0b?style=flat-square)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-64748b?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourname/lumilog?style=flat-square&color=fde68a)](https://github.com/yourname/lumilog/stargazers)

<br/>

> *"Your diary should know you — not just store you."*

</div>

---

LumiLog is a **floating desktop pet + AI diary** that sits quietly in the corner of your screen. Speak your day, and it does four things at once: transcribes in ~1 second, reflects back something real, extracts reminders automatically, and—if you asked a question inside your entry—**answers it from your diary history**.

```
You:    "I'm exhausted. Also, what did I do last week?"

灵犀:   [Reflection]  You've been running hard — this is the third week
                      you've mentioned feeling drained. ✦

        [Memory]      Last week: finished the design doc on Tuesday, had
                      back-to-back calls Wednesday, and took a half-day
                      Friday. You seemed lighter by the end of it.
```

**Everything runs on your machine. Your diary never leaves.**

---

## Why LumiLog?

| | LumiLog | Notion / Apple Notes | Day One |
|---|---|---|--|
| Voice → text in ~1s | ✅ | ❌ | 💰 premium |
| AI that *reads* your entries | ✅ local LLM | ❌ | ❌ |
| Answers memory questions inline | ✅ unified flow | ❌ | ❌ |
| Conversation memory across turns | ✅ 20-turn context | ❌ | ❌ |
| Local, Groq, or OpenAI LLM | ✅ pick any | ❌ | ❌ |
| 100% private, runs offline | ✅ (Ollama mode) | ❌ cloud | ❌ cloud |
| Cute pet on your desktop | ✅ animated ✦star | 😐 | 😐 |

---

## Features

### 🐾 Desktop Pet — Now with ✦ Star & Paws
An animated chibi companion drawn entirely with geometry — no image files. New design: rounder head, glassy layered eyes, star hair accessory that pulses, paws and curly tail.

```
idle       →  breathing sway, random blinks
listening  →  animated waveform bars (red) above head while recording
thinking   →  spinning star orbit while LLM processes
happy      →  sparkles, ^‿^ smile, bounce
sleepy     →  Zzz bubbles after 10 min idle, auto-wakes on any touch
```

### 🎙️ Voice-First, ~1 Second Transcription
Hit record. Talk in Chinese, English, Japanese, or mix freely. [Groq Whisper](https://console.groq.com) transcribes in about one second — auto-detects language by default. No setup required.

### 🧠 Unified Intent Detection — Diary + Memory in One Shot

The key design: **one LLM call** reads your input and decides what it is.

- Sharing your day → reflection + tag extraction  
- Asking a question → memory retrieval answer  
- Both in the same sentence → both, simultaneously  

```
"Had a great gym session today!"           → diary reflection
"What was I stressed about last week?"     → memory retrieval
"I'm tired. What's my schedule tomorrow?"  → diary + reminder lookup
```

Results appear in separate labeled boxes in the Write tab — no tab-switching needed.

### 🔌 Choose Your LLM — Ollama, Groq, OpenAI, or Custom

```env
LLM_PROVIDER=ollama   # local, fully private (default)
LLM_PROVIDER=groq     # cloud, very fast, free tier
LLM_PROVIDER=openai   # GPT-4o-mini, etc.
LLM_PROVIDER=custom   # any OpenAI-compatible endpoint
```

### ⏰ Reminders Extracted Automatically
Write naturally. Reminders are parsed with `dateparser` (instant — no extra LLM call):
```
"Meeting with Tom tomorrow at 10"    → ⏰ 2026-03-04 10:00
"Call dentist next Monday morning"   → ⏰ 2026-03-09 09:00
```

### 💬 Stateful Chat Tab
Rolling 20-turn conversation history. Follow-up questions work:
```
"What was I stressed about?"   → [answers]
"Tell me more about that."     → [refers back to previous answer]
```

---

## Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | Ollama · Groq · OpenAI · custom | Your choice — local privacy or cloud speed |
| STT | [Groq Whisper](https://console.groq.com) | ~10× faster than OpenAI Whisper. Free tier. |
| SDK | `openai` Python package | One package handles all providers (OpenAI-compatible API) |
| DB | SQLite + FTS5 | Indexed full-text search. Zero config. One portable file. |
| Time parsing | `dateparser` | Natural language → datetime instantly, no LLM call |
| GUI | `tkinter` + Canvas | Ships with Python. Pet sprite is pure geometry. |

---

## Getting Started

### Prerequisites

- Python 3.11+
- A free [Groq API key](https://console.groq.com) (for Whisper STT)
- For Ollama mode: [Ollama](https://ollama.com) installed and running

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

**Ollama (local, private):**
```env
GROQ_API_KEY=your_groq_key_here
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
```

**Groq (cloud, fast, free tier):**
```env
GROQ_API_KEY=your_groq_key_here
LLM_PROVIDER=groq
LLM_API_KEY=your_groq_key_here
LLM_MODEL=llama-3.3-70b-versatile
```

### Run

```bash
# Ollama only: pull a model first
ollama pull llama3.2 && ollama serve

python main.py
```

Pet appears in the **bottom-right corner**. Click to open the diary panel.

---

## How to Use

| Action | What happens |
|--------|-------------|
| **Click** the pet | Opens / closes the diary panel |
| **Right-click** | Menu: record, set mood, quit |
| **Drag** anywhere | Move it to your preferred corner |
| **🎙️ Record** | Start → waveform appears → stop → ~1s transcription |
| **Save & Reflect** | Unified LLM: reflection + any memory query answered |
| **Chat tab** | Stateful 20-turn conversation with 灵犀 |

### Memory queries (in the Write tab or Chat tab)

```
"What did I do last week?"
"When did I last write about the gym?"
"What's coming up this month?"
"Summarise my month"
"What was I excited about?" 
```

---

## Project Structure

```
lumilog/
├── main.py                        Entry point — wires all callbacks
├── env.example                    All config options documented
├── requirements.txt
└── modules/
    ├── llm_client.py              Multi-provider: Ollama/Groq/OpenAI/custom
    ├── ai_brain.py                Unified intent: diary + memory in one LLM call
    ├── memory.py                  3-stage pipeline: plan → FTS5 retrieve → answer
    ├── database.py                SQLite + FTS5 full-text search
    ├── voice.py                   Mic capture + Groq Whisper STT
    ├── reminder_scheduler.py      Background thread: fires due reminders
    └── pet_window.py              Animated chibi pet + 4-tab panel UI
```

---

## Privacy

- **Ollama mode:** entirely local. Zero external calls except Groq STT (audio only — no diary text).
- **Groq/OpenAI mode:** diary entries sent to cloud LLM. Choose based on your preference.

---

## Roadmap

- [ ] Semantic / vector memory (embeddings → "that stressful project" style queries)
- [ ] VAD auto-stop (silence detection — no manual stop button)
- [ ] Mood tracking + weekly chart
- [ ] Weekly AI summary reports
- [ ] Export diary as Markdown or PDF
- [ ] Cloud sync via Supabase (opt-in)

---

<div align="center">
<sub>Built with Python · Runs local · Your diary stays yours.</sub>
<br/>
<sub>✦ Star if you like it — it helps others find it ✦</sub>
</div>

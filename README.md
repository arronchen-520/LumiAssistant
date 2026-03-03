<div align="center">

# ✦ 小记 · Xiaoji

### Your AI diary companion that lives on your desktop

*Speak your day. Let it remember. Let it care.*

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-3b82f6?style=flat-square&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/LLM-Ollama%20%28local%29-a78bfa?style=flat-square)
![Groq](https://img.shields.io/badge/STT-Groq%20Whisper-34d399?style=flat-square)
![SQLite](https://img.shields.io/badge/Storage-SQLite-f59e0b?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-64748b?style=flat-square)

</div>

---

Xiaoji is a **desktop pet + AI diary** that sits quietly in the corner of your screen. Click it open to speak or type your day, and it will reflect back something meaningful — not generic affirmations, but real observations grounded in what you actually wrote.

It remembers. Ask it *"what was I worried about last week?"* and it goes back through your entries, finds the pattern, and answers like a friend who was there.

Everything runs locally. Your diary never leaves your machine.

```
You: "I'm exhausted. Had three back-to-back meetings and the project still isn't done."
     "Remind me to follow up with Sarah on Friday at 3pm."

Xiaoji: Today sounds genuinely draining — carrying both the weight of the work
        and the feeling that it's not moving fast enough is a lot. I've set a
        reminder for Friday at 3pm to follow up with Sarah. ✦
```

---

## Features

**🐾 Desktop Pet**
A floating, animated character that lives on your screen. Drag it anywhere. It breathes, blinks, bounces when happy, and shows Zzz when idle too long. Right-click for quick actions.

**🎙️ Voice-First Journaling**
Hit record, talk naturally. [Groq Whisper](https://console.groq.com) transcribes in ~1 second. The entry lands in the text box — clean, accurate, ready to save.

**💭 AI Reflection**
After saving, your local Ollama model reads what you wrote and responds with a short, grounded reflection. It notices things you might have glossed over.

**🧠 Memory System**
Your entries are indexed. The AI uses a two-stage pipeline to answer questions about your past:
1. A query planner reads your question and generates a structured search (date range, keywords, or task lookup)
2. SQLite retrieves the matching entries
3. The LLM synthesizes a natural answer from real data

```
"What did I do last week?"           → date-range query
"When did I last mention the gym?"   → keyword search
"What's coming up this month?"       → reminder lookup
```

**⏰ Smart Reminders**
Write *"remind me to call mom on Sunday"* anywhere in your diary entry. The AI extracts the intent and time, and a popup fires when the moment arrives.

**💬 Chat Interface**
A persistent conversation tab where you can ask anything. The pet has read your journal — it answers with context.

---

## Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | [Ollama](https://ollama.com) (local) | Fully private. No API cost. Swap models freely. |
| STT | [Groq Whisper](https://console.groq.com) | ~10× faster than OpenAI Whisper. Free tier. |
| SDK | `openai` Python package | Both Ollama and Groq expose OpenAI-compatible APIs. One package for everything. |
| DB | SQLite | Zero config. Your data in one portable file. |
| GUI | `tkinter` + Canvas | Ships with Python. The pet sprite is drawn with geometry — no image files needed. |

---

## Getting Started

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running
- A free [Groq API key](https://console.groq.com)

**macOS / Linux — system audio:**
```bash
# macOS
brew install portaudio

# Ubuntu / Debian
sudo apt-get install python3-tk portaudio19-dev
```

### Install

```bash
git clone https://github.com/yourname/xiaoji
cd xiaoji

pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
```

Edit `.env`:
```env
GROQ_API_KEY=your_key_here     # from console.groq.com
OLLAMA_MODEL=llama3.2          # or mistral, qwen2.5, gemma3, etc.
```

### Pull a model and start Ollama

```bash
ollama pull llama3.2
ollama serve          # keep this running in a terminal
```

### Run

```bash
python main.py
```

The pet appears in the **bottom-right corner** of your screen.

---

## How to Use

| Action | What happens |
|--------|-------------|
| **Click** the pet | Opens / closes the diary panel |
| **Right-click** the pet | Quick menu (record, change mood, quit) |
| **Drag** the pet | Move it anywhere on screen |
| **🎙️ Record** button | Hold to record, click again to stop + transcribe |
| **Save & Reflect** | Saves entry, triggers AI reflection, extracts reminders |
| **Chat tab** | Ask anything — memory queries or casual conversation |

### Memory queries that work

```
"What did I do yesterday?"
"Summarize last week for me"
"When did I last write about work stress?"
"What do I have coming up next week?"
"Did I write anything about the gym?"
"What was on my mind last month?"
```

### Setting reminders naturally

Just write it in your diary:
```
"Meeting with Tom tomorrow at 10am"
"Remember to submit the report by Friday"
"Call dentist next Monday morning"
```
Xiaoji parses the time and fires a popup when the moment arrives.

---

## Project Structure

```
xiaoji/
├── main.py                       Entry point
├── .env.example
├── requirements.txt
├── data/
│   └── diary.db                  SQLite database (auto-created)
└── modules/
    ├── llm_client.py             Shared OpenAI SDK client → Ollama
    ├── ai_brain.py               Diary analysis, time parsing, chat routing
    ├── memory.py                 LLM query planner + SQLite retrieval pipeline
    ├── database.py               All DB access (context-managed connections)
    ├── voice.py                  Recording + Groq Whisper transcription
    ├── reminder_scheduler.py     Background thread: fires due reminders
    └── pet_window.py             Desktop pet sprite + full panel UI
```

### Memory pipeline in detail

```
User: "What did I do last week?"
        │
        ▼
  is_memory_query()          — keyword pre-filter (fast, no LLM)
        │ yes
        ▼
  _plan_query()              — Ollama, temp=0: parse intent → structured JSON
  { "query_type": "date_range",
    "date_start": "2026-02-23",
    "date_end":   "2026-03-01" }
        │
        ▼
  _retrieve()                — SQL: fetch matching entries from SQLite
        │
        ▼
  _generate_answer()         — Ollama, temp=0.7: synthesize warm reply
        │
        ▼
  "Last week you had three work meetings and were worried about..."
```

---

## Roadmap

- [ ] Embeddings + vector search (semantic memory: *"that stressful period"*)
- [ ] Weekly / monthly AI summary reports
- [ ] Export diary as Markdown or PDF
- [ ] Custom pet skins / Live2D integration
- [ ] Multi-language diary (auto-detect per entry)
- [ ] Cloud sync via Supabase (opt-in)
- [ ] Mood timeline chart

---

## Privacy

All diary data is stored in `data/diary.db` on your local machine. LLM inference runs entirely through Ollama — **no diary content is ever sent to a cloud API**. The only external calls are:
- Groq Whisper: receives raw audio for transcription (no text, no diary content)

---

## Contributing

Issues and PRs welcome. This is an early-stage personal project — if you build something with it or have ideas, open a discussion.

---

<div align="center">
<sub>Built with Python, Ollama, and the belief that your diary should stay yours.</sub>
</div>

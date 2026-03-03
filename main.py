"""
main.py — LumiLog 灵犀笔记
Stack: OpenAI SDK → Ollama (LLM) + OpenAI SDK → Groq (Whisper STT) + SQLite
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# Validate required keys before importing anything else
_GROQ_KEY = os.getenv("GROQ_API_KEY", "")
if not _GROQ_KEY or _GROQ_KEY.startswith("your_"):
    sys.exit(
        "❌  GROQ_API_KEY not set.\n"
        "    Get a free key at https://console.groq.com and add it to .env"
    )

from modules.database           import init_db, save_entry, get_entries, get_upcoming_reminders, save_reminder
from modules.voice              import VoiceRecorder
from modules.ai_brain           import analyze_entry, parse_reminder_time, chat_with_pet
from modules.reminder_scheduler import ReminderScheduler
from modules.pet_window         import DesktopPet


def main():
    init_db()
    print("✅  Database ready")

    try:
        recorder = VoiceRecorder()
    except ValueError as e:
        sys.exit(f"❌  {e}")

    # Read STT language from env (default: auto-detect)
    stt_language = os.getenv("STT_LANGUAGE", "").strip() or None

    # ── Callbacks wired from UI → logic ──────────────────────────────────────

    def on_record_start():
        recorder.start()

    def on_record_stop() -> str:
        wav = recorder.stop()
        if not wav:
            return ""
        print("🎙️  Transcribing via Groq Whisper...")
        text = recorder.transcribe(wav, language=stt_language)
        print(f"📝  {text!r}")
        return text

    def on_save_entry(text: str) -> dict:
        recent = get_entries(limit=5)
        print("🤖  Analyzing entry with Ollama...")
        result = analyze_entry(text, context_entries=recent)
        print(f"    reflection: {result.get('reflection', '')[:60]!r}")

        saved_reminders = []
        for r in result.get("reminders", []):
            msg  = r.get("message", "").strip()
            desc = r.get("time_description", "").strip()
            if msg and desc:
                dt = parse_reminder_time(desc)
                if dt:
                    save_reminder(dt, msg)
                    saved_reminders.append({"message": msg})
                    print(f"    ⏰  reminder saved: {msg!r} @ {dt}")

        save_entry(
            raw_text=text,
            ai_reflection=result.get("reflection", ""),
            tags=result.get("summary_tags", []),
        )
        result["reminders"] = saved_reminders
        return result

    def on_chat(message: str) -> str:
        recent = get_entries(limit=10)
        return chat_with_pet(message, recent_entries=recent)

    # ── Build UI ──────────────────────────────────────────────────────────────

    pet = DesktopPet(
        on_record_start=on_record_start,
        on_record_stop=on_record_stop,
        on_chat=on_chat,
        get_entries=lambda: get_entries(limit=50),
        get_reminders=lambda: get_upcoming_reminders(limit=20),
    )
    pet.set_save_callback(on_save_entry)

    # ── Reminder scheduler ────────────────────────────────────────────────────

    def on_reminder_fire(message: str):
        pet.root.after(0, lambda: pet.show_reminder_popup(message))

    scheduler = ReminderScheduler(on_reminder_callback=on_reminder_fire)
    scheduler.start()

    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    lang  = stt_language or "auto"
    print(f"\n🌟  LumiLog 灵犀笔记 is running!")
    print(f"    LLM : Ollama ({model})  →  localhost:11434")
    print(f"    STT : Groq Whisper large-v3-turbo (language={lang})")
    print(f"    DB  : SQLite  →  data/diary.db  [FTS5 enabled]")
    print(f"\n    Click the pet to open the diary panel.")
    print(f"    Right-click for the menu.  Ctrl+C to quit.\n")

    try:
        pet.run()
    except KeyboardInterrupt:
        print("\n👋  Bye!")
    finally:
        scheduler.stop()


if __name__ == "__main__":
    main()

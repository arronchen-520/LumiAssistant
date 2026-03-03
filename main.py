"""
main.py — LumiLog 灵犀笔记
Stack: LLM (Ollama / Groq / OpenAI / custom) + Groq Whisper STT + SQLite + FTS5
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# Validate Groq STT key
_GROQ_KEY = os.getenv("GROQ_API_KEY", "")
if not _GROQ_KEY or _GROQ_KEY.startswith("your_"):
    sys.exit(
        "❌  GROQ_API_KEY not set.\n"
        "    Get a free key at https://console.groq.com and add it to .env"
    )

from modules.database           import init_db, save_entry, get_entries, get_upcoming_reminders, save_reminder
from modules.voice              import VoiceRecorder
from modules.ai_brain           import process_input, parse_reminder_time, chat_with_pet
from modules.llm_client         import get_provider_info
from modules.reminder_scheduler import ReminderScheduler
from modules.pet_window         import DesktopPet


def main():
    init_db()
    print("✅  Database ready")

    try:
        recorder = VoiceRecorder()
    except ValueError as e:
        sys.exit(f"❌  {e}")

    stt_language = os.getenv("STT_LANGUAGE", "").strip() or None

    # ── Callbacks ─────────────────────────────────────────────────────────────

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
        """
        统一输入处理: 单次 LLM 调用同时判断意图（日记/记忆查询/两者）。
        Unified input processing: one LLM call handles diary + memory query.
        """
        recent = get_entries(limit=10)
        print("🤖  Processing input (unified intent detection)...")
        result = process_input(text, context_entries=recent)

        input_type = result.get("input_type", "diary")
        print(f"    type: {input_type}")

        if result.get("query_answer"):
            print(f"    query_answer: {result['query_answer'][:60]!r}")
        if result.get("reflection"):
            print(f"    reflection: {result['reflection'][:60]!r}")

        # 提醒解析与存储
        saved_reminders = []
        for r in result.get("reminders", []):
            msg  = r.get("message", "").strip()
            desc = r.get("time_description", "").strip()
            if msg and desc:
                dt = parse_reminder_time(desc)
                if dt:
                    save_reminder(dt, msg)
                    saved_reminders.append({"message": msg})
                    print(f"    ⏰  reminder: {msg!r} @ {dt}")

        # 无论是日记还是查询，都存储原始输入
        save_entry(
            raw_text=text,
            ai_reflection=result.get("reflection") or result.get("query_answer") or "",
            tags=result.get("summary_tags", []),
        )
        result["reminders"] = saved_reminders
        return result

    def on_chat(message: str) -> str:
        recent = get_entries(limit=10)
        return chat_with_pet(message, recent_entries=recent)

    # ── UI ────────────────────────────────────────────────────────────────────

    pet = DesktopPet(
        on_record_start=on_record_start,
        on_record_stop=on_record_stop,
        on_chat=on_chat,
        get_entries=lambda: get_entries(limit=50),
        get_reminders=lambda: get_upcoming_reminders(limit=20),
    )
    pet.set_save_callback(on_save_entry)

    # ── Reminder Scheduler ────────────────────────────────────────────────────

    def on_reminder_fire(message: str):
        pet.root.after(0, lambda: pet.show_reminder_popup(message))

    scheduler = ReminderScheduler(on_reminder_callback=on_reminder_fire)
    scheduler.start()

    info  = get_provider_info()
    lang  = stt_language or "auto"
    print(f"\n🌟  LumiLog 灵犀笔记 is running!")
    print(f"    LLM : {info['provider'].upper()} ({info['model']})  →  {info['url']}")
    print(f"    STT : Groq Whisper large-v3-turbo  (language={lang})")
    print(f"    DB  : SQLite + FTS5  →  data/diary.db")
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

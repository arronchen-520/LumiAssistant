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
        统一输入处理: 单次 LLM 调用同时判断意图，支持 7 种 input_type
        Unified input processing: 7 intents supported in one shot.
        """
        recent = get_entries(limit=7)
        print("🤖  Processing input (unified intent detection)...")
        result = process_input(text, context_entries=recent)

        input_type = result.get("input_type", "diary")
        print(f"    type: {input_type}")

        if result.get("query_answer"):
            print(f"    query_answer: {result['query_answer'][:60]!r}")
        if result.get("reflection"):
            print(f"    reflection: {result['reflection'][:60]!r}")

        # ── Commands ──
        if input_type == "command":
            commands = result.get("command_list", [])
            from modules.database import (
                delete_last_entry, delete_entry_by_date, update_entry_by_date,
                delete_reminder_by_keyword, update_reminder_by_keyword
            )
            messages = []
            for cmd in commands:
                action = cmd.get("action")
                if action == "delete_last_entry":
                    success = delete_last_entry()
                    messages.append("🗑️ 已为你删除上一条日记。" if success else "没有可以删除的日记哦。")
                elif action == "delete_entry_by_date":
                    count = delete_entry_by_date(cmd.get("target_date"))
                    messages.append(f"🗑️ 已删除了 {count} 条日记。" if count else "没有找到那天的日记。")
                elif action == "update_entry_by_date":
                    count = update_entry_by_date(cmd.get("target_date"), cmd.get("new_text"))
                    messages.append(f"✅ 已更新了日记内容。" if count else "没有找到那天的日记。")
                elif action == "delete_reminder":
                    count = delete_reminder_by_keyword(cmd.get("target_keyword"))
                    messages.append(f"🗑️ 已删除了相关提醒。" if count else "没有找到该提醒。")
                elif action == "update_reminder":
                    count = update_reminder_by_keyword(cmd.get("target_keyword"), cmd.get("new_time"))
                    messages.append(f"✅ 已更新提醒时间。" if count else "没有找到该提醒。")
                else:
                    messages.append(f"收到未知的命令。")
            
            result["reflection"] = "\n".join(messages) if messages else "收到命令（未识别执行细节）。"
            return result

        # ── Persona Update ──
        if input_type == "persona_update":
            from modules.database import upsert_persona
            updates = result.get("persona_updates", [])
            for u in updates:
                k, v = u.get("key"), u.get("value")
                if k and v:
                    upsert_persona(k, v)
                    print(f"    🧠  persona: {k} = {v}")
            result["reflection"] = "📝 我已经悄悄记在心里啦！"
            return result

        # ── Chit-chat / Brainstorm ──
        # Do NOT save these transient interactions to the diary database
        if input_type in ("chit-chat", "brainstorm"):
            return result

        # ── Diary / Query / Both ──
        # Parse reminders if present
        saved_reminders = []
        for r in result.get("reminders", []):
            msg  = r.get("message", "").strip()
            desc = r.get("time_description", "").strip()
            if msg and desc:
                dt = parse_reminder_time(desc)
                if dt:
                    from modules.database import save_reminder
                    save_reminder(dt, msg)
                    saved_reminders.append({"message": msg})
                    print(f"    ⏰  reminder: {msg!r} @ {dt}")

        # Save entry to SQLite
        from modules.database import save_entry
        
        diary_date = result.get("diary_date")
        created_at = None
        if diary_date:
            try:
                # Add current time to the user-specified date to make it a valid timestamp
                created_at = f"{diary_date} {datetime.now().strftime('%H:%M:%S')}"
            except Exception:
                pass
                
        save_entry(
            raw_text=text,
            ai_reflection=result.get("reflection") or result.get("query_answer") or "",
            tags=result.get("summary_tags", []),
            created_at=created_at,
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

    def on_reminder_fire(rid: int, message: str):
        pet.root.after(0, lambda: pet.show_reminder_popup(rid, message))

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

"""
reminder_scheduler.py - Background thread polling for due reminders
"""
import threading
import time
from modules.database import get_pending_reminders, mark_reminder_done


class ReminderScheduler:
    def __init__(self, on_reminder_callback):
        self._callback = on_reminder_callback
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            try:
                for r in get_pending_reminders():
                    mark_reminder_done(r[0])
                    self._callback(r[2])
            except Exception as e:
                print(f"[Scheduler] {e}")
            time.sleep(30)

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
        self._notified_ids = set()

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            try:
                # get_pending_reminders returns (id, remind_at, message)
                for r in get_pending_reminders():
                    rid = r[0]
                    if rid not in self._notified_ids:
                        self._notified_ids.add(rid)
                        msg = r[2]
                        # Pass both ID and message so the UI can mark it done later
                        self._callback(rid, msg)
            except Exception as e:
                print(f"[Scheduler] {e}")
            time.sleep(30)

"""
database.py - SQLite storage with proper connection management.
All connections are opened/closed via context managers — no leaks.
"""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "diary.db"


@contextmanager
def _db():
    """Context manager that opens, yields, commits, and closes."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # access columns by name
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with _db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS entries (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at   TEXT NOT NULL,
                raw_text     TEXT NOT NULL,
                ai_reflection TEXT,
                tags         TEXT
            );
            CREATE TABLE IF NOT EXISTS reminders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                remind_at  TEXT NOT NULL,
                message    TEXT NOT NULL,
                done       INTEGER DEFAULT 0
            );
        """)


# ── Entries ───────────────────────────────────────────────────────────────────

def save_entry(raw_text: str, ai_reflection: str = "", tags: list = None) -> int:
    with _db() as conn:
        cur = conn.execute(
            "INSERT INTO entries (created_at, raw_text, ai_reflection, tags) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), raw_text, ai_reflection,
             json.dumps(tags or [], ensure_ascii=False)),
        )
        return cur.lastrowid


def get_entries(limit: int = 50) -> list[dict]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, created_at, raw_text, ai_reflection, tags "
            "FROM entries ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [_entry_row(r) for r in rows]


def get_entries_by_date(start: str, end: str) -> list[dict]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, created_at, raw_text, ai_reflection, tags "
            "FROM entries WHERE date(created_at) BETWEEN ? AND ? ORDER BY created_at ASC",
            (start, end),
        ).fetchall()
    return [_entry_row(r) for r in rows]


def get_entries_by_keywords(keywords: list[str], limit: int = 15) -> list[dict]:
    if not keywords:
        return []
    cond   = " OR ".join(["raw_text LIKE ? OR ai_reflection LIKE ?"] * len(keywords))
    params = [p for kw in keywords for p in (f"%{kw}%", f"%{kw}%")]
    with _db() as conn:
        rows = conn.execute(
            f"SELECT id, created_at, raw_text, ai_reflection, tags "
            f"FROM entries WHERE {cond} ORDER BY created_at DESC LIMIT ?",
            params + [limit],
        ).fetchall()
    return [_entry_row(r) for r in rows]


def _entry_row(r) -> dict:
    return {
        "id":         r["id"],
        "date":       r["created_at"][:16],
        "text":       r["raw_text"],
        "reflection": r["ai_reflection"] or "",
        "tags":       r["tags"] or "[]",
    }


# ── Reminders ─────────────────────────────────────────────────────────────────

def save_reminder(remind_at: datetime, message: str) -> int:
    with _db() as conn:
        cur = conn.execute(
            "INSERT INTO reminders (created_at, remind_at, message) VALUES (?,?,?)",
            (datetime.now().isoformat(), remind_at.isoformat(), message),
        )
        return cur.lastrowid


def get_pending_reminders() -> list[tuple]:
    """Reminders whose time has passed and are not yet done."""
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, remind_at, message FROM reminders "
            "WHERE remind_at <= ? AND done = 0",
            (datetime.now().isoformat(),),
        ).fetchall()
    return [(r["id"], r["remind_at"], r["message"]) for r in rows]


def get_upcoming_reminders(limit: int = 20) -> list[dict]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, remind_at, message FROM reminders "
            "WHERE remind_at > ? AND done = 0 ORDER BY remind_at ASC LIMIT ?",
            (datetime.now().isoformat(), limit),
        ).fetchall()
    return [{"id": r["id"], "time": r["remind_at"][:16], "message": r["message"]} for r in rows]


def get_upcoming_reminders_window(days: int = 30) -> list[dict]:
    from datetime import timedelta
    now   = datetime.now()
    until = (now + timedelta(days=days)).isoformat()
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, remind_at, message FROM reminders "
            "WHERE remind_at > ? AND remind_at <= ? AND done = 0 ORDER BY remind_at ASC",
            (now.isoformat(), until),
        ).fetchall()
    return [{"id": r["id"], "time": r["remind_at"][:16], "message": r["message"]} for r in rows]


def mark_reminder_done(rid: int):
    with _db() as conn:
        conn.execute("UPDATE reminders SET done = 1 WHERE id = ?", (rid,))

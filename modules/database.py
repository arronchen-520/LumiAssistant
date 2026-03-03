"""
database.py - SQLite storage with FTS5 full-text search.

Improvements over v1:
  - FTS5 virtual table for fast keyword search (replaces LIKE %keyword% brute-force)
  - Trigger keeps FTS in sync with entries on INSERT
  - get_entries_by_keywords() now uses FTS5 MATCH — orders-of-magnitude faster at scale
  - All connections context-managed — no leaks
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
    # Enable FTS5 (built into Python's sqlite3 on all platforms)
    conn.execute("PRAGMA journal_mode=WAL")
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

            -- FTS5 full-text search index over diary entries
            CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
                raw_text,
                ai_reflection,
                content='entries',
                content_rowid='id',
                tokenize='unicode61'
            );

            -- Persona table for long-term agent memory
            CREATE TABLE IF NOT EXISTS persona (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            -- Keep FTS in sync: populate on insert
            CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
                INSERT INTO entries_fts(rowid, raw_text, ai_reflection)
                VALUES (new.id, new.raw_text, COALESCE(new.ai_reflection, ''));
            END;

            -- Rebuild FTS for any rows that existed before the trigger was created
            -- (safe to run multiple times — INSERT OR IGNORE skips existing rowids)
        """)

        # Backfill FTS for pre-existing rows (idempotent)
        conn.execute("""
            INSERT OR IGNORE INTO entries_fts(rowid, raw_text, ai_reflection)
            SELECT id, raw_text, COALESCE(ai_reflection, '') FROM entries
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

def delete_last_entry() -> bool:
    """Deletes the most recent diary entry. Returns True if deleted."""
    with _db() as conn:
        row = conn.execute("SELECT id FROM entries ORDER BY id DESC LIMIT 1").fetchone()
        if row:
            conn.execute("DELETE FROM entries WHERE id = ?", (row["id"],))
            conn.execute("DELETE FROM entries_fts WHERE rowid = ?", (row["id"],))
            return True
        return False

# ── Persona ───────────────────────────────────────────────────────────────────

def upsert_persona(key: str, value: str):
    """Updates or inserts a persona setting for long-term agent memory."""
    with _db() as conn:
        conn.execute("INSERT OR REPLACE INTO persona (key, value) VALUES (?, ?)", (key, value))

def get_all_personas() -> dict[str, str]:
    """Returns all persona settings as a dictionary."""
    with _db() as conn:
        rows = conn.execute("SELECT key, value FROM persona").fetchall()
        return {r["key"]: r["value"] for r in rows}


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


def get_entries_by_keywords(keywords: list[str], limit: int = 20) -> list[dict]:
    """
    Full-text search using FTS5 MATCH — much faster than LIKE at scale.
    Falls back to LIKE if FTS5 table doesn't exist (e.g., old DB).
    Increased default limit from 15 → 20.
    """
    if not keywords:
        return []

    # Build FTS5 query: join keywords with OR
    fts_query = " OR ".join(f'"{kw}"' for kw in keywords)

    with _db() as conn:
        try:
            rows = conn.execute(
                """
                SELECT e.id, e.created_at, e.raw_text, e.ai_reflection, e.tags
                FROM entries e
                JOIN entries_fts f ON e.id = f.rowid
                WHERE entries_fts MATCH ?
                ORDER BY e.created_at DESC
                LIMIT ?
                """,
                (fts_query, limit),
            ).fetchall()
            return [_entry_row(r) for r in rows]
        except sqlite3.OperationalError:
            # FTS5 not available — fall back to LIKE
            cond   = " OR ".join(["raw_text LIKE ? OR ai_reflection LIKE ?"] * len(keywords))
            params = [p for kw in keywords for p in (f"%{kw}%", f"%{kw}%")]
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

def get_reminders_by_date(start: str, end: str) -> list[dict]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, remind_at, message FROM reminders "
            "WHERE date(remind_at) >= ? AND date(remind_at) <= ? AND done = 0 ORDER BY remind_at ASC",
            (start, end),
        ).fetchall()
    return [{"id": r["id"], "time": r["remind_at"][:16], "message": r["message"]} for r in rows]

def mark_reminder_done(rid: int):
    with _db() as conn:
        conn.execute("UPDATE reminders SET done = 1 WHERE id = ?", (rid,))

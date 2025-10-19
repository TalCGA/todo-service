import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().with_name("todo.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    # Turn on SQLite foreign key enforcement
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db() -> None:
    schema = """
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT CHECK(status IN ('open','in_progress','done')) NOT NULL DEFAULT 'open',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """
    with get_conn() as conn:
        conn.executescript(schema)

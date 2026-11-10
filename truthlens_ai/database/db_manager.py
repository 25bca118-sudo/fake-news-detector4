import sqlite3
from pathlib import Path

from truthlens_ai.config import DATABASE_PATH


def get_db_connection():
    """Return a configured SQLite connection."""
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db():
    schema_file = Path(__file__).with_name("schema.sql")
    with get_db_connection() as conn:
        conn.executescript(schema_file.read_text(encoding="utf-8"))


def execute_insert(query, params=()):
    with get_db_connection() as conn:
        cursor = conn.execute(query, params)
        return cursor.lastrowid


def execute_query(query, params=()):
    with get_db_connection() as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def execute_scalar(query, params=()):
    with get_db_connection() as conn:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row is not None else None


def execute_update(query, params=()):
    with get_db_connection() as conn:
        conn.execute(query, params)

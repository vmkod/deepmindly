from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from core.config import settings


def _ensure_parent_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    _ensure_parent_dir(settings.db_path)
    conn = sqlite3.connect(settings.db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    finally:
        conn.close()


def init_db():
    with db_cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS window_titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                cluster_index INTEGER
            )
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_window_titles_created_at
            ON window_titles (created_at)
            """
        )
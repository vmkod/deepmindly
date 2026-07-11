from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .connect import db_cursor, init_db


@dataclass(frozen=True)
class WindowRecord:
    id: int
    title: str
    created_at: str
    cluster_id: Optional[int]


def save_window_title(title: str):
    init_db()
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO window_titles (title) VALUES (?)",
            (title,),
        )


def fetch_all_titles():
    init_db()
    with db_cursor() as cur:
        cur.execute(
            "SELECT id, title, created_at, cluster_id FROM window_titles ORDER BY created_at"
        )
        rows = cur.fetchall()
    return [WindowRecord(*row) for row in rows]
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .connect import db_cursor, init_db


@dataclass(frozen=True)
class WindowRecord:
    id: int
    title: str
    created_at: str
    cluster_index: Optional[int]


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
            "SELECT id, title, created_at, cluster_index FROM window_titles ORDER BY created_at"
        )
        rows = cur.fetchall()
    return [WindowRecord(*row) for row in rows]


def update_cluster_assignments(assignments: Dict[int, int]):
    if not assignments:
        return
    with db_cursor() as cur:
        cur.executemany(
            "UPDATE window_titles SET cluster_index = ? WHERE id = ?",
            [(cluster_index, record_id) for record_id, cluster_index in assignments.items()],
        )
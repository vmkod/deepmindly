from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from .connect import db_cursor, init_db

_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

_MAX_GAP_SECONDS = 90 * 60  # Максимальное неактивное время (в секундах)


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


def compute_durations(records: List[WindowRecord]):
    if not records:
        return {}

    ordered = sorted(records, key=lambda r: r.created_at)
    timestamps = [datetime.strptime(r.created_at, _TIMESTAMP_FORMAT) for r in ordered]

    durations: Dict[int, float] = {}
    for i in range(len(ordered) - 1):
        gap_seconds = (timestamps[i + 1] - timestamps[i]).total_seconds()
        durations[ordered[i].id] = min(gap_seconds, _MAX_GAP_SECONDS)

    last_gap_seconds = (datetime.now() - timestamps[-1]).total_seconds()
    durations[ordered[-1].id] = min(max(last_gap_seconds, 0.0), _MAX_GAP_SECONDS)

    return durations
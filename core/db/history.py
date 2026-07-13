from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List

from .connect import db_cursor, init_db


@dataclass(frozen=True)
class ClusterSnapshot:
    cluster_index: int
    name: str
    size: int
    top_titles: List[str]


@dataclass(frozen=True)
class AnalysisRun:
    run_id: int
    run_date: str  # 'YYYY-MM-DD'
    clusters: List[ClusterSnapshot]


def init_history_tables():
    init_db()
    with db_cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL REFERENCES analysis_runs(id),
                cluster_index INTEGER NOT NULL,
                name TEXT NOT NULL,
                size INTEGER NOT NULL,
                top_titles TEXT NOT NULL
            )
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_analysis_runs_date ON analysis_runs (run_date)"
        )


def save_run(run_date: str, clusters: List[ClusterSnapshot]):
    init_history_tables()
    with db_cursor() as cur:
        cur.execute("SELECT id FROM analysis_runs WHERE run_date = ?", (run_date,))
        existing = cur.fetchone()

        if existing:
            run_id = existing[0]
            cur.execute("DELETE FROM analysis_clusters WHERE run_id = ?", (run_id,))
        else:
            cur.execute("INSERT INTO analysis_runs (run_date) VALUES (?)", (run_date,))
            run_id = cur.lastrowid

        cur.executemany(
            """
            INSERT INTO analysis_clusters (run_id, cluster_index, name, size, top_titles)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (run_id, c.cluster_index, c.name, c.size, json.dumps(c.top_titles, ensure_ascii=False))
                for c in clusters
            ],
        )


def get_run(run_date: str):
    init_history_tables()
    with db_cursor() as cur:
        cur.execute("SELECT id FROM analysis_runs WHERE run_date = ?", (run_date,))
        row = cur.fetchone()
        if row is None:
            return None
        run_id = row[0]

        cur.execute(
            "SELECT cluster_index, name, size, top_titles FROM analysis_clusters WHERE run_id = ?",
            (run_id,),
        )
        cluster_rows = cur.fetchall()

    clusters = [
        ClusterSnapshot(
            cluster_index=cluster_index,
            name=name,
            size=size,
            top_titles=json.loads(top_titles_json),
        )
        for cluster_index, name, size, top_titles_json in cluster_rows
    ]
    return AnalysisRun(run_id=run_id, run_date=run_date, clusters=clusters)


def list_runs(limit: int = 365):
    init_history_tables()
    with db_cursor() as cur:
        cur.execute(
            "SELECT run_date FROM analysis_runs ORDER BY run_date DESC LIMIT ?",
            (limit,),
        )
        return [row[0] for row in cur.fetchall()]


def rename_cluster(run_date: str, cluster_index: int, new_name: str):
    init_history_tables()
    with db_cursor() as cur:
        cur.execute("SELECT id FROM analysis_runs WHERE run_date = ?", (run_date,))
        row = cur.fetchone()
        if row is None:
            return False
        run_id = row[0]

        cur.execute(
            "UPDATE analysis_clusters SET name = ? WHERE run_id = ? AND cluster_index = ?",
            (new_name, run_id, cluster_index),
        )
        return cur.rowcount > 0
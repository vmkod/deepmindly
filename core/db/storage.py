from __future__ import annotations
from .connect import db_cursor, init_db


def save_window_title(title: str):
    init_db()
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO window_titles (title) VALUES (?)",
            (title,),
        )
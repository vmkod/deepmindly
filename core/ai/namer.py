from __future__ import annotations

from typing import List

_MAX_NAME_LENGTH = 40


def name_cluster(top_titles: List[str]):
    if not top_titles:
        return "Без названия"

    name = top_titles[0]
    if len(name) > _MAX_NAME_LENGTH:
        name = name[: _MAX_NAME_LENGTH - 1].rstrip() + "…"
    return name

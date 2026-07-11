from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Settings:
    watch_interval: int
    db_path: Path


def _find_config_path(filename: str = "config.yaml"):
    here = Path(__file__).resolve().parent
    for candidate_dir in [here, *here.parents]:
        candidate = candidate_dir / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Не удалось найти {filename}. Убедитесь, что файл существует в корне проекта."
    )


def load_settings():
    config_path = _find_config_path()

    with config_path.open("r", encoding="utf-8") as f:
        raw: dict = yaml.safe_load(f) or {}

    watcher_cfg: dict = raw.get("watcher", {})
    db_cfg: dict = raw.get("database", {})

    db_path = Path(db_cfg.get("path", "data/deepmindly.db"))
    if not db_path.is_absolute():
        db_path = config_path.parent / db_path

    return Settings(
        watch_interval=int(watcher_cfg.get("interval_seconds", 5)),
        db_path=db_path
    )


settings = load_settings()
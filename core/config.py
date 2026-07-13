from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Settings:
    watch_interval: int
    db_path: Path
    ai_model_name: str
    ai_n_clusters: int
    ai_top_n_titles: int
    log_level: str
    log_file: Path


def _find_config_path(filename: str = "config.yaml"):
    here = Path(__file__).resolve().parent
    for candidate_dir in [here, *here.parents]:
        candidate = candidate_dir / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Не удалось найти {filename}."
    )


def load_settings():
    config_path = _find_config_path()

    with config_path.open("r", encoding="utf-8") as f:
        raw: dict = yaml.safe_load(f) or {}

    watcher_cfg: dict = raw.get("watcher", {})
    db_cfg: dict = raw.get("database", {})
    ai_cfg: dict = raw.get("ai", {})
    logging_cfg: dict = raw.get("logging", {})

    db_path = Path(db_cfg.get("path", "data/deepmindly.db"))
    if not db_path.is_absolute():
        db_path = config_path.parent / db_path

    log_file = Path(logging_cfg.get("file", "data/logs/deepmindly.log"))
    if not log_file.is_absolute():
        log_file = config_path.parent / log_file

    return Settings(
        watch_interval=int(watcher_cfg.get("interval_seconds", 3)),
        db_path=db_path,
        ai_model_name=str(ai_cfg.get("model_name", "all-MiniLM-L6-v2")),
        ai_n_clusters=int(ai_cfg.get("n_clusters", 3)),
        ai_top_n_titles=int(ai_cfg.get("top_n_titles", 3)),
        log_level=str(logging_cfg.get("level", "INFO")).upper(),
        log_file=log_file
    )


settings = load_settings()
from __future__ import annotations

import sys

from loguru import logger

from core.config import settings

_configured = False


def setup_logging():
    global _configured
    if _configured:
        return

    logger.remove()

    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<dim>{time:HH:mm:ss}</dim> | <level>{level: <8}</level> | {message}",
        colorize=True,
    )

    settings.log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        settings.log_file,
        level=settings.log_level,
        rotation="5 MB",
        retention=5,
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    _configured = True
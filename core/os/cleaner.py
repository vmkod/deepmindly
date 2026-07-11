from __future__ import annotations

import re


_TELEGRAM_UNREAD_PREFIX = re.compile(r"^\(\d+\)\s*")
_TELEGRAM_UNREAD_SUFFIX = re.compile(r"\s*[-—–]\s*\(\d+\)$")

_EDGE_SUFFIX = re.compile(r"\s*[-—–]\s*Личный:\s*Microsoft\s*Edge$", re.IGNORECASE)

_BROWSER_NAMES = r"Google\s+Chrome|Mozilla\s+Firefox|Яндекс\s+Браузер|Opera|Brave"
_BROWSER_SUFFIX = re.compile(rf"\s*[-—–]\s*({_BROWSER_NAMES})$", re.IGNORECASE)

_IGNORE_KEYWORDS = {
    "новая вкладка", "экспресс-панель", "новая приватная вкладка",
    "private new tab", "новое окно",
    "проводник", "диспетчер задач", "параметры", "поиск",
    "загрузки", "рабочий стол", "корзина",
}


def clean_title(raw_title: str):
    if not raw_title or not raw_title.strip():
        return ""

    cleaned = (
        raw_title.replace("\u200e", "")
        .replace("\u200b", "")
        .replace("\xa0", " ")
        .strip()
    )

    # Счётчики непрочитанных сообщений Telegram
    cleaned = _TELEGRAM_UNREAD_PREFIX.sub("", cleaned)
    cleaned = _TELEGRAM_UNREAD_SUFFIX.sub("", cleaned)

    # Суффиксы названий браузеров
    cleaned = _EDGE_SUFFIX.sub("", cleaned)
    cleaned = _BROWSER_SUFFIX.sub("", cleaned)

    cleaned = cleaned.strip()

    if cleaned.lower() in _IGNORE_KEYWORDS or len(cleaned) < 3:
        return ""

    return cleaned
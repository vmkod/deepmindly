from __future__ import annotations

import time
import win32gui

from core.config import settings
from core.db import save_window_title
from .cleaner import clean_title


def start_watching():
    print(
        f"[*] Запуск трекера. Интервал: {settings.watch_interval} сек. (Ctrl+C для остановки)"
    )

    last_title: str = ""

    try:
        while True:
            hwnd = win32gui.GetForegroundWindow()
            raw_title: str = win32gui.GetWindowText(hwnd)

            cleaned_title = clean_title(raw_title)

            if cleaned_title and cleaned_title != last_title:
                save_window_title(cleaned_title)
                print(f"[+] Сохранено: {cleaned_title}")
                last_title = cleaned_title

            time.sleep(settings.watch_interval)
    except KeyboardInterrupt:
        print("\n[*] Трекер остановлен.")
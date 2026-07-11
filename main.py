from __future__ import annotations

from core.db import fetch_all_titles
from core.os import start_watching


def main():
    print("=============")
    print("🧠 DEEPMINDLY")
    print("=============")

    try:
        start_watching()
    finally:
        titles = fetch_all_titles()

        for record in titles:
            print(f"- {record}")


if __name__ == "__main__":
    main()
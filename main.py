from __future__ import annotations

import argparse

from core.db import fetch_all_titles
from core.os import start_watching


def run_watch():
    start_watching()


def show_all_titles():
    titles = fetch_all_titles()

    for record in titles:
        print(f"- {record}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="deepmindly",
        description="DeepMindly — локальный AI-трекер продуктивности",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--watch", action="store_true", help="Запустить фоновый сбор данных"
    )
    group.add_argument(
        "--titles", action="store_true", help="Показать все записи"
    )
    return parser


def main():
    print("=============")
    print("🧠 DEEPMINDLY")
    print("=============")

    parser = build_parser()
    args = parser.parse_args()

    if args.watch:
        run_watch()
    elif args.titles:
        show_all_titles()


if __name__ == "__main__":
    main()
from __future__ import annotations

import argparse

from core.ai.brain import ClusterBrain
from core.ai.vectors import encode_titles
from core.db import fetch_all_titles, update_cluster_assignments
from core.os import start_watching


def run_watch():
    start_watching()


def run_analyze():
    records = fetch_all_titles()

    if len(records) < 3:
        print(
            "Недостаточно данных. Сначала запустите --watch"
        )
        return

    titles = [record.title for record in records]

    print(f"Загружено {len(titles)} заголовков. Строим эмбеддинги...")
    embeddings = encode_titles(titles)

    print("Кластеризуем активность...")
    brain = ClusterBrain()
    labels = brain.fit(embeddings)

    assignments = {record.id: int(label) for record, label in zip(records, labels)}
    update_cluster_assignments(assignments)

    summaries = brain.summarize(titles, embeddings)

    print("\n===== Результаты кластеризации =====")
    for summary in summaries:
        print(f"\nКластер #{summary.cluster_id} — {summary.size} записей")
        for i, title in enumerate(summary.top_titles, start=1):
            print(f"   {i}. {title}")


def show_all_titles():
    titles = fetch_all_titles()

    for record in titles:
        print(f"- {record}")


def vectorization():
    titles = fetch_all_titles()

    if not titles:
        print("Недостаточно данных. Сначала запустите --watch")
        return

    raw_titles = [record.title for record in titles]
    test_titles = list(set(raw_titles))[:3]

    print(f"\nБерем для теста {len(test_titles)} уникальных заголовка(ов):")
    for idx, t in enumerate(test_titles, 1):
        print(f"  {idx}. {t}")

    print("\nЗапуск модели и кодирование...")

    embeddings = encode_titles(test_titles)

    print("\n===== Результаты векторизации =====")
    print(f"Форма матрицы: {embeddings.shape}")

    for i, title in enumerate(test_titles):
        vector = embeddings[i]
        vector_preview = vector[:5]

        print(f"\nЗаголовок: '{title}'")
        print(f"  Первые 5 чисел (скалярные веса): {vector_preview}")


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
    group.add_argument(
        "--vectorization", action="store_true", help="Проверить работу векторизации"
    )
    group.add_argument(
        "--analyze", action="store_true", help="Запустить кластеризацию"
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
    elif args.vectorization:
        vectorization()
    elif args.analyze:
        run_analyze()


if __name__ == "__main__":
    main()
from __future__ import annotations

import argparse
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.ai.brain import ClusterBrain
from core.ai.vectors import encode_titles
from core.config import settings
from core.db import fetch_all_titles, update_cluster_assignments
from core.os import start_watching

console = Console()


def run_watch():
    start_watching()


def run_analyze():
    print("Загрузка истории заголовков из базы данных...")
    records = fetch_all_titles()

    if len(records) < 3:
        console.print(
            Panel(
                f"Недостаточно данных для анализа (найдено записей: {len(records)}).\n"
                "Сначала запустите [bold]python main.py --watch[/bold], чтобы накопить историю.",
                title="⚠ DeepMindly",
                style="yellow",
            )
        )
        return

    titles = [record.title for record in records]
    print(f"Загружено {len(titles)} заголовков. Строим эмбеддинги ({settings.ai_model_name})...")
    embeddings = encode_titles(titles)

    print(f"Кластеризация методом K-Means (n_clusters={settings.ai_n_clusters})...")
    brain = ClusterBrain()
    labels = brain.fit(embeddings)

    assignments = {record.id: int(label) for record, label in zip(records, labels)}
    update_cluster_assignments(assignments)

    summaries = brain.summarize(titles, embeddings)
    print(f"Готово: выделено {len(summaries)} кластеров.")

    _render_clusters_table(summaries)


def _render_clusters_table(summaries: List):
    table = Table(
        title="DeepMindly — Текущий анализ активности",
        show_lines=True,
        title_style="bold magenta",
    )
    table.add_column("#", justify="right", style="dim")
    table.add_column("Кластер ID", style="bold")
    table.add_column("Записей", justify="right")
    table.add_column("Типичные заголовки")

    ordered = sorted(summaries, key=lambda s: s.size, reverse=True)

    for position, summary in enumerate(ordered, start=1):
        top_titles_block = "\n".join(f"• {t}" for t in summary.top_titles)
        table.add_row(
            str(position),
            f"Кластер #{summary.cluster_id}",
            str(summary.size),
            top_titles_block
        )

    console.print(table)
    total_records = sum(s.size for s in ordered)
    console.print(f"[dim]Всего записей: {total_records} | Кластеров: {len(ordered)}[/dim]")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="deepmindly",
        description="DeepMindly — локальный AI-трекер продуктивности",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--watch", action="store_true", help="Запустить фоновый сбор данных")
    group.add_argument("--analyze", action="store_true", help="Запустить кластеризацию и вывести результаты")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.watch:
        run_watch()
    elif args.analyze:
        run_analyze()


if __name__ == "__main__":
    main()
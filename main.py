from __future__ import annotations

import argparse
from datetime import date
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.ai.brain import ClusterBrain
from core.ai.namer import name_cluster
from core.ai.vectors import encode_titles
from core.config import settings
from core.db import fetch_all_titles, update_cluster_assignments
from core.db.history import ClusterSnapshot, get_run, list_runs, rename_cluster, save_run
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
                "Сначала запустите [bold]main.py --watch[/bold], чтобы накопить историю.",
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

    snapshots = [
        ClusterSnapshot(
            cluster_index=summary.cluster_id,
            name=name_cluster(summary.top_titles),
            size=summary.size,
            top_titles=summary.top_titles
        )
        for summary in summaries
    ]

    today = date.today().isoformat()
    save_run(today, snapshots)

    _render_clusters_table(snapshots, today)
    console.print(
        "\n[dim]Подсказка: [bold]main.py --history[/bold] — посмотреть прошлые дни и переименовать активности.[/dim]"
    )


def run_history():
    dates = sorted(list_runs())
    if not dates:
        console.print(
            Panel(
                "Сохранённых анализов пока нет. Запустите [bold]main.py --analyze[/bold].",
                title="⚠ DeepMindly",
                style="yellow",
            )
        )
        return

    index = len(dates) - 1
    console.print(
        "[dim]Команды: [bold]n[/bold] — следующий день · [bold]p[/bold] — предыдущий день · "
        "[bold]r[/bold] — переименовать активность · [bold]q[/bold] — выход[/dim]\n"
    )

    while True:
        run_date = dates[index]
        run = get_run(run_date)
        if run is None:
            console.print(f"[red]Не удалось загрузить данные за {run_date}.[/red]")
            break

        order = _render_clusters_table(run.clusters, run.run_date)
        console.print(f"[dim]День {index + 1} из {len(dates)}[/dim]")

        command = console.input("\n[bold]> [/bold]").strip().lower()
        console.print()

        if command == "n":
            if index < len(dates) - 1:
                index += 1
            else:
                console.print("[yellow]Это последний день в истории.[/yellow]\n")
        elif command == "p":
            if index > 0:
                index -= 1
            else:
                console.print("[yellow]Это первый день в истории.[/yellow]\n")
        elif command == "r":
            _rename_cluster_interactive(run.run_date, order)
        elif command == "q":
            break
        else:
            console.print("[red]Неизвестная команда. Используйте n / p / r / q.[/red]\n")


def _rename_cluster_interactive(run_date: str, order: List[int]):
    raw_number = console.input(f"Номер строки для переименования (1-{len(order)}): ").strip()
    try:
        position = int(raw_number)
    except ValueError:
        console.print("[red]Введите число.[/red]\n")
        return

    if not (1 <= position <= len(order)):
        console.print("[red]Нет строки с таким номером.[/red]\n")
        return

    cluster_index = order[position - 1]
    new_name = console.input("Новое название для этой активности: ").strip()
    if not new_name:
        console.print("[red]Название не может быть пустым.[/red]\n")
        return

    if rename_cluster(run_date, cluster_index, new_name):
        console.print(f"[green]Готово! Название успешно сохранено.[/green]\n")
    else:
        console.print("[red]Не удалось обновить имя в базе.[/red]\n")


def _render_clusters_table(clusters: List[ClusterSnapshot], run_date: str):
    table = Table(
        title=f"DeepMindly — анализ активности за {run_date}",
        show_lines=True,
        title_style="bold magenta",
    )
    table.add_column("Номер строки", justify="center", style="bold yellow")
    table.add_column("Активность", style="bold green")
    table.add_column("Записей", justify="center")
    table.add_column("Типичные заголовки")

    ordered = sorted(clusters, key=lambda c: c.size, reverse=True)
    for position, cluster in enumerate(ordered, start=1):
        top_titles_block = "\n".join(f"• {t}" for t in cluster.top_titles)
        table.add_row(str(position), cluster.name, str(cluster.size), top_titles_block)

    console.print(table)
    total_records = sum(c.size for c in ordered)
    console.print(f"[dim]Всего записей: {total_records} | Активностей: {len(ordered)}[/dim]")

    return [c.cluster_index for c in ordered]


def build_parser():
    parser = argparse.ArgumentParser(
        prog="deepmindly",
        description="DeepMindly — локальный AI-трекер активности",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--watch", action="store_true", help="Запустить фоновый сбор данных")
    group.add_argument("--analyze", action="store_true", help="Запустить кластеризацию и сохранить снимок за сегодня")
    group.add_argument("--history", action="store_true", help="Просмотреть снимки анализа по дням")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.watch:
        run_watch()
    elif args.analyze:
        run_analyze()
    elif args.history:
        run_history()


if __name__ == "__main__":
    main()
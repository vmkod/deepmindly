from __future__ import annotations

import pandas as pd
import streamlit as st

from core.db.history import get_run, list_runs
from core.formatting import format_duration, render_time_bar

st.set_page_config(page_title="DeepMindly", page_icon="🧠", layout="wide")
st.title("🧠 DeepMindly - анализ активности по дням")

available_dates = list_runs()

if not available_dates:
    st.warning(
        "Сохранённых анализов пока нет. Запустите `main.py --analyze`, "
        "чтобы создать первый снимок."
    )
    st.stop()

selected_date = st.selectbox("Выберите день", available_dates)
run = get_run(selected_date)

if run is None or not run.clusters:
    st.info("Для этого дня нет данных.")
    st.stop()

clusters = sorted(run.clusters, key=lambda c: c.duration_seconds, reverse=True)
total_duration = sum(c.duration_seconds for c in clusters)

col1, col2, col3 = st.columns(3)
col1.metric("Общее время", format_duration(total_duration))
col2.metric("Записей за день", sum(c.size for c in clusters))
col3.metric("Активностей", len(clusters))

clusters_df = pd.DataFrame(
    [
        {
            "Активность": c.name,
            "Время": format_duration(c.duration_seconds),
            "Доля": render_time_bar(
                (c.duration_seconds / total_duration) if total_duration > 0 else 0.0
            ),
            "Минут": round(c.duration_seconds / 60, 1),
            "Записей": c.size,
            "Типичные заголовки": ", ".join(c.top_titles),
        }
        for c in clusters
    ]
)

clusters_df.index = range(1, len(clusters_df) + 1)
clusters_df.index.name = "№"

st.subheader("Время по активностям")
st.bar_chart(clusters_df.set_index("Активность")["Минут"])

st.subheader("Детали")
st.dataframe(clusters_df.drop(columns=["Минут"]), width="stretch")
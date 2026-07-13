from __future__ import annotations

import pandas as pd
import streamlit as st

from core.db.history import get_run, list_runs

st.set_page_config(page_title="DeepMindly", page_icon="🧠", layout="wide")
st.title("🧠 DeepMindly — анализ активности по дням")

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

clusters = sorted(run.clusters, key=lambda c: c.size, reverse=True)

col1, col2 = st.columns(2)
col1.metric("Записей за день", sum(c.size for c in clusters))
col2.metric("Кластеров", len(clusters))

clusters_df = pd.DataFrame(
    [
        {
            "Кластер": c.name,
            "Записей": c.size,
            "Типичные заголовки": ", ".join(c.top_titles),
        }
        for c in clusters
    ]
)

st.bar_chart(clusters_df.set_index("Кластер")["Записей"])
st.dataframe(clusters_df, width="stretch")
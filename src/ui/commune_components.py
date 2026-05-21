"""Streamlit components for the Commune Portal."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import line_chart, ranked_bar_chart
from src.formatting import format_delta, format_value
from src.ui_components import download_csv, section_header


def metric_card(label: str, value: float | None, *, period: str | None = None, trend: dict | None = None) -> None:
    delta = None
    if trend and trend.get("delta") is not None:
        delta = format_delta(trend.get("delta"), "number")
    st.metric(label, format_value(value, "number"), delta=delta, help=f"Latest period: {period}" if period else None)


def empty_topic(topic: str) -> None:
    st.info(f"No commune-level data is currently available for {topic.lower()} in the connected datasets.")


def render_commune_trend(item: dict, key: str) -> None:
    dataset = item["dataset"]
    rows = item.get("rows", pd.DataFrame())
    if rows.empty or dataset.time_column not in rows.columns or dataset.value_column not in rows.columns:
        st.info("There is no time trend available for this dataset yet.")
        return
    chart_df = rows[[dataset.time_column, dataset.value_column]].copy()
    chart_df[dataset.value_column] = pd.to_numeric(chart_df[dataset.value_column], errors="coerce")
    chart_df = (
        chart_df.dropna(subset=[dataset.value_column])
        .groupby(dataset.time_column, as_index=False)[dataset.value_column]
        .mean()
        .sort_values(dataset.time_column)
    )
    if chart_df.empty:
        st.info("There is no chartable value for this commune in this dataset.")
        return
    fig = line_chart(chart_df, dataset.time_column, dataset.value_column, title="How this commune changed over time")
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{key}_trend")
    download_csv(chart_df, f"{key}_trend.csv", "Download data", key=f"download_{key}_trend")


def render_ranking(item: dict, key: str) -> None:
    rank = item.get("rank")
    if not rank or rank.get("ranking") is None:
        st.info("A commune ranking is not available for this dataset.")
        return
    ranking = rank["ranking"]
    dataset = item["dataset"]
    st.caption(f"Rank {rank['rank']} of {rank['total']} communes for the latest available period.")
    fig = ranked_bar_chart(ranking.head(20), ranking.columns[0], dataset.value_column, top_n=20, title="Where this commune ranks")
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{key}_ranking")
    download_csv(ranking, f"{key}_ranking.csv", "Download ranking", key=f"download_{key}_ranking")


def render_dataset_details(items: list[dict], *, key_prefix: str) -> None:
    for idx, item in enumerate(items):
        dataset = item["dataset"]
        latest = item.get("latest")
        with st.container(border=True):
            st.markdown(f"#### {dataset.title}")
            st.caption(dataset.description or "Official STATEC / LUSTAT dataset.")
            cols = st.columns(3)
            with cols[0]:
                metric_card("Latest value", latest.get("value") if latest else None, period=latest.get("period") if latest else None, trend=item.get("trend"))
            with cols[1]:
                comparison = item.get("comparison") or {}
                metric_card("Compared with average", comparison.get("difference"), period=comparison.get("period"))
            with cols[2]:
                rank = item.get("rank") or {}
                st.metric("Rank", f"{rank.get('rank')} / {rank.get('total')}" if rank else "Not available")
            render_commune_trend(item, key=f"{key_prefix}_{idx}")
            with st.expander("Source details", expanded=False):
                st.write(f"**Source:** STATEC / LUSTAT")
                st.write(f"**Dataset ID:** `{dataset.dataset_id}`")
                st.write(f"**Topic:** {dataset.topic}")
                st.write(f"**Geography column:** `{dataset.geography_column or 'auto-detected'}`")
                st.write(dataset.notes or "No extra caveat has been added yet.")
                rows = item.get("rows", pd.DataFrame())
                if not rows.empty:
                    st.dataframe(rows.head(100), use_container_width=True, hide_index=True)


def render_all_data_table(profile: dict) -> None:
    data = pd.DataFrame(profile.get("available_datasets", []))
    if data.empty:
        st.info("No commune-level dataset metadata has been added yet.")
        return
    topic_options = ["All"] + sorted(data["Topic"].dropna().unique().tolist())
    topic = st.selectbox("Filter by topic", topic_options)
    query = st.text_input("Search commune datasets", placeholder="population, housing, labour...")
    filtered = data.copy()
    if topic != "All":
        filtered = filtered[filtered["Topic"] == topic]
    if query.strip():
        q = query.strip().casefold()
        filtered = filtered[filtered.apply(lambda row: q in " ".join(map(str, row.values)).casefold(), axis=1)]
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    download_csv(filtered, f"{profile['commune']}_commune_datasets.csv", "Download commune dataset list")


def render_section_items(title: str, items: list[dict], key_prefix: str) -> None:
    section_header(title)
    if not items:
        empty_topic(title)
        return
    render_dataset_details(items, key_prefix=key_prefix)

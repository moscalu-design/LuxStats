"""Deterministic salary/dataflow explorer, preserved as an advanced page."""

from __future__ import annotations

import duckdb
import pandas as pd
import streamlit as st

from src.analytics import execute_plan
from src.cache import (
    DUCKDB_PATH,
    fetch_and_cache_dataset,
    get_dataset_meta,
    is_dataset_cached,
    list_cached_datasets,
    load_dataset,
    load_dataflows,
    table_name_for,
)
from src.charts import bar_chart, line_chart
from src.metadata import get_dataset_metadata
from src.statec_client import SALARY_KEYWORDS, StatecClient, filter_salary_related
from src.ui_components import data_source_info, download_csv


@st.cache_resource
def get_client() -> StatecClient:
    return StatecClient()


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def cached_dataflows(_client: StatecClient, refresh_token: int = 0):
    return load_dataflows(_client, force_refresh=refresh_token > 0)


def render_salaries_page() -> None:
    st.markdown("##### Raw salary dataset explorer")
    st.caption(
        "Browse official STATEC / LUSTAT salary, wage and income datasets. "
        "Download one, then preview, chart, filter, and export the cached data. "
        "Pick a dataset from the sidebar to begin."
    )
    client = get_client()
    flow, _pool = salary_sidebar(client)
    if flow is None:
        st.info("Pick a dataflow from the sidebar to begin.")
        return

    df = dataset_panel(client, flow)
    if df is None or df.empty:
        return
    quick_chart_panel(flow.id, df)
    with st.expander("Advanced deterministic query", expanded=False):
        query_panel(flow, df)


def salary_sidebar(client: StatecClient):
    if "refresh_token" not in st.session_state:
        st.session_state["refresh_token"] = 0

    if st.sidebar.button("Refresh dataflow list"):
        st.session_state["refresh_token"] += 1

    with st.spinner("Loading dataflows..."):
        try:
            flows = cached_dataflows(client, st.session_state["refresh_token"])
        except Exception as exc:
            st.sidebar.error("Could not load live dataflows right now.")
            with st.sidebar.expander("Advanced details", expanded=False):
                st.code(str(exc))
            return None, []

    st.sidebar.write(f"**{len(flows)} dataflows** available from LU1")
    salary_only = st.sidebar.checkbox(
        "Salary / wage / income themes only",
        value=True,
        help="Filter on: " + ", ".join(SALARY_KEYWORDS[:8]) + "...",
    )
    query = st.sidebar.text_input("Search live dataflows", placeholder="salary, gender, commune")

    pool = filter_salary_related(flows) if salary_only else flows
    if query:
        terms = [term for term in query.split() if term]
        pool = [flow for flow in pool if flow.matches(terms)]
    pool = sorted(pool, key=lambda flow: flow.id)

    st.sidebar.write(f"{len(pool)} match")
    selected = st.sidebar.selectbox(
        "Dataflow",
        options=pool,
        format_func=lambda flow: flow.display,
        index=0 if pool else None,
        placeholder="Select a dataflow...",
    )

    with st.sidebar.expander("Cached datasets", expanded=False):
        cached_df = list_cached_datasets()
        if cached_df.empty:
            st.write("Nothing cached yet.")
        else:
            st.dataframe(cached_df, use_container_width=True, hide_index=True)

    return selected, pool


def dataset_panel(client: StatecClient, flow) -> pd.DataFrame | None:
    st.subheader(flow.display)
    st.caption(f"Dataflow ID `{flow.id}` · agency `{flow.agency}` · version `{flow.version}`")

    cached = is_dataset_cached(flow.id)
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        download_label = "Refresh dataset" if cached else "Download dataset"
        if st.button(download_label, type="primary"):
            with st.spinner("Fetching data from LUSTAT..."):
                try:
                    df, csv_path = fetch_and_cache_dataset(client, flow, force_refresh=True)
                    st.success(f"Cached {len(df):,} rows in {csv_path.name}")
                except Exception as exc:
                    st.error("This dataset could not be downloaded right now.")
                    with st.expander("Advanced details", expanded=False):
                        st.code(str(exc))
                    return None
    with col2:
        if cached and st.button("Clear from cache"):
            con = duckdb.connect(str(DUCKDB_PATH))
            try:
                con.execute(f'DROP TABLE IF EXISTS "{table_name_for(flow.id)}"')
                con.execute("DELETE FROM _meta_datasets WHERE dataset_id = ?", [flow.id])
            finally:
                con.close()
            st.rerun()

    if not is_dataset_cached(flow.id):
        st.info("Download the dataset to start exploring.")
        return None

    df = load_dataset(flow.id)
    meta = get_dataset_metadata(flow.id, df)
    data_source_info(
        dataset_name=meta["dataset_name"],
        dataset_id=flow.id,
        source=meta["source"],
        latest_period=meta["latest_period"],
        last_fetched=meta["last_fetched"],
        row_count=meta["row_count"],
        columns=meta["columns"],
        notes=meta["notes"],
    )
    st.write(f"**{len(df):,} rows** · {len(df.columns)} columns")
    with st.expander("Preview first 200 rows", expanded=False):
        st.dataframe(df.head(200), use_container_width=True, hide_index=True)
    with col3:
        download_csv(df, f"{flow.id}.csv", "Download raw dataset")
    return df


def quick_chart_panel(dataset_id: str, df: pd.DataFrame) -> None:
    st.subheader("Quick chart")
    if "OBS_VALUE" not in df.columns:
        st.warning("This dataset does not expose a numeric value column that can be charted automatically.")
        return
    available_dims = [col for col in df.columns if col != "OBS_VALUE" and not col.endswith("_LABEL")]
    default_x = "TIME_PERIOD" if "TIME_PERIOD" in available_dims else (available_dims[0] if available_dims else None)
    if not default_x:
        return
    col1, col2, col3 = st.columns(3)
    with col1:
        x_col = st.selectbox("Choose the horizontal axis", available_dims, index=available_dims.index(default_x))
    with col2:
        color_options = ["None"] + [col for col in available_dims if col != x_col]
        color_col = st.selectbox("Compare groups", color_options)
    with col3:
        chart_type = st.selectbox("Chart type", ["Line", "Bar"])

    chart_df = df[[x_col, "OBS_VALUE"] + ([] if color_col == "None" else [color_col])].dropna(subset=["OBS_VALUE"])
    group_cols = [x_col] + ([] if color_col == "None" else [color_col])
    chart_df = chart_df.groupby(group_cols, as_index=False)["OBS_VALUE"].mean().sort_values(x_col)
    color = None if color_col == "None" else color_col
    fig = line_chart(chart_df, x_col, "OBS_VALUE", color=color, title=f"{dataset_id}: average value") if chart_type == "Line" else bar_chart(chart_df, x_col, "OBS_VALUE", color=color, title=f"{dataset_id}: average value")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Values are averaged when more than one record shares the same visible filters.")
    download_csv(chart_df, f"{dataset_id}_quick_chart.csv")


def query_panel(flow, df: pd.DataFrame) -> None:
    st.write(
        "Build a grouped table from the cached dataset. This is deterministic: "
        "the selected columns become a validated DuckDB query."
    )
    if "OBS_VALUE" not in df.columns:
        st.info("This dataset has no `OBS_VALUE` column to aggregate.")
        return

    dimension_candidates = [col for col in df.columns if col != "OBS_VALUE"]
    defaults = [col for col in ("TIME_PERIOD", "GENDER_LABEL", "SEX_LABEL", "NACE_REV2_LABEL") if col in dimension_candidates]
    dimensions = st.multiselect(
        "Group by",
        dimension_candidates,
        default=defaults[:2],
        key=f"det_dims_{flow.id}",
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        aggregation = st.selectbox("Aggregation", ["avg", "sum", "median", "min", "max", "count"], key=f"det_agg_{flow.id}")
    with col2:
        chart_type = st.selectbox("Chart", ["table", "line", "bar"], key=f"det_chart_{flow.id}")
    with col3:
        limit = st.number_input("Row limit", min_value=10, max_value=5000, value=500, step=50, key=f"det_limit_{flow.id}")

    sort = []
    if "TIME_PERIOD" in dimensions:
        sort.append({"column": "TIME_PERIOD", "order": "asc"})
    plan = {
        "filters": {},
        "dimensions": dimensions,
        "measures": ["OBS_VALUE"],
        "aggregation": aggregation,
        "sort": sort,
        "limit": int(limit),
        "chart": {
            "type": chart_type,
            "x": dimensions[0] if dimensions else None,
            "y": "OBS_VALUE",
            "color": dimensions[1] if len(dimensions) > 1 else None,
        },
        "explanation": "Grouped official dataset query built from explicit controls.",
    }

    try:
        result = execute_plan(plan, flow.id, list(df.columns))
    except Exception as exc:
        st.error("Could not execute this query. Open advanced details for the technical error.")
        with st.expander("Advanced details", expanded=False):
            st.code(str(exc))
        return

    for warning in result.warnings:
        st.warning(warning)
    with st.expander("Generated SQL", expanded=False):
        st.code(result.sql, language="sql")
    st.dataframe(result.df, use_container_width=True, hide_index=True)
    if not result.df.empty:
        download_csv(result.df, f"{flow.id}_query.csv", "Download result")
        _render_chart(result.df, plan.get("chart") or {})


def _render_chart(df: pd.DataFrame, chart: dict) -> None:
    chart_type = (chart.get("type") or "table").lower()
    x = chart.get("x") if chart.get("x") in df.columns else None
    y = chart.get("y") if chart.get("y") in df.columns else None
    color = chart.get("color") if chart.get("color") in df.columns else None
    if chart_type == "table" or not x or not y:
        return
    try:
        fig = line_chart(df, x=x, y=y, color=color) if chart_type == "line" else bar_chart(df, x=x, y=y, color=color)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.warning(f"Could not render chart: {exc}")

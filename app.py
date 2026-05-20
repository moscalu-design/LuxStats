"""Streamlit UI for exploring LUSTAT (STATEC Luxembourg) salary statistics."""

from __future__ import annotations

import json
import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from analytics import execute_plan
from cache import (
    fetch_and_cache_dataset,
    get_dataset_meta,
    is_dataset_cached,
    list_cached_datasets,
    load_dataset,
    load_dataflows,
    schema_for_llm,
)
from llm_planner import plan_query
from statec_client import SALARY_KEYWORDS, StatecClient, filter_salary_related

load_dotenv()

# Streamlit Community Cloud puts secrets in st.secrets, not env vars.
# Mirror them into os.environ so llm_planner.py reads them uniformly.
try:
    for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"):
        if key in st.secrets and not os.environ.get(key):
            os.environ[key] = str(st.secrets[key])
except Exception:
    # No secrets.toml locally — that's fine, .env / shell env take over.
    pass

st.set_page_config(page_title="LuxStats — STATEC explorer", layout="wide")


@st.cache_resource
def get_client() -> StatecClient:
    return StatecClient()


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def cached_dataflows(_client: StatecClient, refresh_token: int = 0):
    return load_dataflows(_client, force_refresh=refresh_token > 0)


def sidebar(client: StatecClient):
    st.sidebar.title("LuxStats")
    st.sidebar.caption("Luxembourg STATEC / LUSTAT salary explorer")

    if "refresh_token" not in st.session_state:
        st.session_state["refresh_token"] = 0

    if st.sidebar.button("Refresh dataflow list"):
        st.session_state["refresh_token"] += 1

    with st.spinner("Loading dataflows…"):
        try:
            flows = cached_dataflows(client, st.session_state["refresh_token"])
        except Exception as exc:
            st.sidebar.error(f"Could not load dataflows: {exc}")
            return None, []

    st.sidebar.write(f"**{len(flows)} dataflows** available from LU1")

    salary_only = st.sidebar.checkbox(
        "Salary / wage / income themes only", value=True,
        help="Filter on: " + ", ".join(SALARY_KEYWORDS[:8]) + "…",
    )
    query = st.sidebar.text_input("Search by keyword", placeholder="e.g. salary, gender, commune")

    pool = filter_salary_related(flows) if salary_only else flows
    if query:
        terms = [t for t in query.split() if t]
        pool = [f for f in pool if f.matches(terms)]
    pool = sorted(pool, key=lambda f: f.id)

    st.sidebar.write(f"{len(pool)} match")
    selected = st.sidebar.selectbox(
        "Dataflow",
        options=pool,
        format_func=lambda f: f.display,
        index=0 if pool else None,
        placeholder="Select a dataflow…",
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
        download_label = "Re-download CSV" if cached else "Download CSV"
        if st.button(download_label, type="primary"):
            with st.spinner("Fetching SDMX-CSV from LUSTAT…"):
                try:
                    df, csv_path = fetch_and_cache_dataset(client, flow, force_refresh=True)
                    st.success(f"Cached {len(df):,} rows → {csv_path.name}")
                except Exception as exc:
                    st.error(f"Download failed: {exc}")
                    return None
    with col2:
        if cached and st.button("Clear from cache"):
            import duckdb
            from cache import DUCKDB_PATH, table_name_for
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
    meta = get_dataset_meta(flow.id) or {}
    st.write(
        f"**{meta.get('row_count', len(df)):,} rows** · "
        f"{len(df.columns)} columns · fetched {meta.get('fetched_at')}"
    )
    with st.expander("Preview (first 200 rows)", expanded=False):
        st.dataframe(df.head(200), use_container_width=True, hide_index=True)
    with col3:
        st.download_button(
            "Export raw dataset CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"{flow.id}.csv",
            mime="text/csv",
        )
    return df


def query_panel(flow, df: pd.DataFrame):
    st.divider()
    st.subheader("Ask a question")
    st.caption(
        "The LLM only emits a JSON query plan. Python and DuckDB do the math, "
        "so what you see is reproducible."
    )

    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.warning(
            "No `ANTHROPIC_API_KEY` set — falling back to a heuristic planner. "
            "Add the key to `.env` to enable natural-language queries.",
            icon="⚠️",
        )

    question = st.text_input(
        "Your question",
        placeholder="e.g. Average wage by gender over time, or median salary by commune in 2022",
        key=f"q_{flow.id}",
    )

    if not question:
        return

    schema = schema_for_llm(flow.id)
    with st.spinner("Planning query…"):
        plan, source = plan_query(question, schema)

    st.markdown(f"**Plan source:** `{source}`")
    if plan.get("explanation"):
        st.markdown(f"_{plan['explanation']}_")

    plan_col, meta_col = st.columns([2, 1])
    with plan_col:
        st.markdown("**Query plan**")
        st.code(json.dumps(plan, ensure_ascii=False, indent=2), language="json")
    with meta_col:
        st.markdown("**Source**")
        st.write(f"Dataset: `{flow.id}`")
        st.write(f"Filters: `{plan.get('filters') or {}}`")
        st.write(f"Dimensions: `{plan.get('dimensions') or []}`")
        st.write(f"Measures: `{plan.get('measures') or []}`")

    try:
        result = execute_plan(plan, flow.id, list(df.columns))
    except Exception as exc:
        st.error(f"Could not execute plan: {exc}")
        return

    if result.warnings:
        for w in result.warnings:
            st.warning(w)

    with st.expander("SQL executed", expanded=False):
        st.code(result.sql, language="sql")

    st.markdown(f"**Result: {len(result.df):,} rows**")
    st.dataframe(result.df, use_container_width=True, hide_index=True)

    if not result.df.empty:
        st.download_button(
            "Export result CSV",
            data=result.df.to_csv(index=False).encode("utf-8"),
            file_name=f"{flow.id}_query.csv",
            mime="text/csv",
            key=f"export_{flow.id}",
        )
        _render_chart(result.df, plan.get("chart") or {})


def _render_chart(df: pd.DataFrame, chart: dict):
    chart_type = (chart.get("type") or "table").lower()
    x = chart.get("x") if chart.get("x") in df.columns else None
    y = chart.get("y") if chart.get("y") in df.columns else None
    color = chart.get("color") if chart.get("color") in df.columns else None
    if chart_type == "table" or not x or not y:
        return
    plot_df = df.copy()
    if x and pd.api.types.is_string_dtype(plot_df[x]):
        # Sort time-like axis lexically — SDMX TIME_PERIOD already sorts well.
        plot_df = plot_df.sort_values(x)
    try:
        if chart_type == "line":
            fig = px.line(plot_df, x=x, y=y, color=color, markers=True)
        elif chart_type == "bar":
            fig = px.bar(plot_df, x=x, y=y, color=color, barmode="group")
        else:
            return
        st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.warning(f"Could not render chart: {exc}")


def main():
    client = get_client()
    flow, _pool = sidebar(client)
    if flow is None:
        st.title("LuxStats")
        st.write("Pick a dataflow from the sidebar to begin.")
        return

    df = dataset_panel(client, flow)
    if df is None or df.empty:
        return
    query_panel(flow, df)


if __name__ == "__main__":
    main()

from __future__ import annotations

import streamlit as st

from src.catalog import catalog_themes, search_catalog
from src.cache import fetch_and_cache_dataset, is_dataset_cached, load_dataset, load_dataflows
from src.charts import bar_chart, line_chart
from src.data.source_catalog import catalog_summary
from src.metadata import get_dataset_metadata
from src.statec_client import StatecClient
from src.ui.page_header import render_page_header
from src.ui.time_controls import apply_time_filter, render_time_controls
from src.ui_components import configure_page, data_source_info, download_csv, render_sidebar

configure_page("LuxStats - Dataset Explorer")
render_sidebar()


@st.cache_resource
def get_client() -> StatecClient:
    return StatecClient()


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def cached_dataflows(_client: StatecClient, refresh_token: int = 0):
    return load_dataflows(_client, force_refresh=refresh_token > 0)


render_page_header("dataset_explorer", eyebrow="Advanced")
st.caption(
    "Use this page for actual API data inspection. Use Source Library for the full source inventory and readiness status."
)

_summary = catalog_summary()
if _summary["total"]:
    with st.container(border=True):
        st.markdown("#### 🗂️ Looking beyond the LUSTAT API?")
        st.caption(
            f"The Source Library catalogs {_summary['total']:,} official sources — "
            f"{_summary['api']:,} LUSTAT API datasets, {_summary['excel']:,} Excel "
            f"data files and {_summary['publications']:,} publication annexes — "
            "categorized and searchable."
        )
        st.page_link("pages/13_Source_Library.py", label="Open the Source Library")

query = st.text_input("Search datasets", placeholder="house prices, wages, population, inflation...")
theme_options = ["All"] + catalog_themes()
theme = st.selectbox("Filter by topic", theme_options)
recommended = st.checkbox("Recommended for dashboards only", value=False)

curated = search_catalog(query=query, theme=theme, recommended_only=recommended)
st.subheader("Curated catalog")
if curated.empty:
    st.info("No curated entries match that search yet. Try a broader term or open live LUSTAT search below.")
else:
    st.dataframe(
        curated[
            [
                "theme",
                "friendly_title",
                "description",
                "dataset_id",
                "geography",
                "update_frequency",
                "recommended",
                "status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )
    selected_catalog_id = st.selectbox(
        "Open curated entry",
        curated["dataset_id"].tolist(),
        format_func=lambda dataset_id: curated.loc[
            curated["dataset_id"] == dataset_id, "friendly_title"
        ].iloc[0],
    )
    entry = curated[curated["dataset_id"] == selected_catalog_id].iloc[0].to_dict()
    data_source_info(
        dataset_name=entry["friendly_title"],
        dataset_id=entry["dataset_id"],
        latest_period=entry["time_periods"],
        last_fetched=None,
        notes=entry["notes"],
    )
    left, right = st.columns(2)
    with left:
        st.write("**Available filters**")
        if entry["dimensions"]:
            for dimension in entry["dimensions"]:
                st.write(f"- {dimension}")
        else:
            st.write("Load or confirm the dataset to inspect available filters.")
    with right:
        st.write("**Search aliases**")
        st.write(", ".join(entry["keywords"]))
    if not str(entry["dataset_id"]).startswith("TODO_CONFIRM"):
        st.caption("This entry has a confirmed-looking ID. Use live search below to fetch and preview it.")
    download_csv(curated, "luxstats_curated_catalog.csv", "Download catalog")

with st.expander("Live LUSTAT dataflow search", expanded=False):
    client = get_client()
    if "explorer_refresh_token" not in st.session_state:
        st.session_state["explorer_refresh_token"] = 0
    if st.button("Refresh dataflow list"):
        st.session_state["explorer_refresh_token"] += 1
    try:
        flows = cached_dataflows(client, st.session_state["explorer_refresh_token"])
    except Exception as exc:
        st.error("Could not load the live LUSTAT dataflow list right now.")
        with st.expander("Advanced details", expanded=False):
            st.code(str(exc))
        flows = []
    live_terms = [term for term in query.split() if term]
    if live_terms:
        flows = [flow for flow in flows if flow.matches(live_terms)]
    st.caption(f"{len(flows)} live matches")
    selected = st.selectbox(
        "Open a live dataflow",
        options=sorted(flows, key=lambda flow: flow.id),
        format_func=lambda flow: flow.display,
        index=0 if flows else None,
        placeholder="Select a dataflow...",
    )
    if selected is not None:
        cached = is_dataset_cached(selected.id)
        if st.button("Fetch or refresh selected dataset", type="primary"):
            with st.spinner("Fetching data from LUSTAT..."):
                try:
                    fetch_and_cache_dataset(client, selected, force_refresh=True)
                    st.success("Dataset cached.")
                except Exception as exc:
                    st.error("This dataset could not be fetched right now.")
                    with st.expander("Advanced details", expanded=False):
                        st.code(str(exc))
        if cached or is_dataset_cached(selected.id):
            df = load_dataset(selected.id)
            meta = get_dataset_metadata(selected.id, df)
            data_source_info(
                dataset_name=meta["dataset_name"],
                dataset_id=selected.id,
                source=meta["source"],
                latest_period=meta["latest_period"],
                last_fetched=meta["last_fetched"],
                row_count=meta["row_count"],
                columns=meta["columns"],
                notes=meta["notes"],
            )
            st.dataframe(df.head(200), use_container_width=True, hide_index=True)
            download_csv(df, f"{selected.id}.csv", "Download full CSV")
            if "TIME_PERIOD" in df.columns and "OBS_VALUE" in df.columns:
                chart_df = df[["TIME_PERIOD", "OBS_VALUE"]].dropna(subset=["OBS_VALUE"])
                chart_df = chart_df.groupby("TIME_PERIOD", as_index=False)["OBS_VALUE"].mean()
                selection = render_time_controls(chart_df, "TIME_PERIOD", f"explorer_{selected.id}", default="Last 10 years")
                chart_df = apply_time_filter(chart_df, "TIME_PERIOD", selection)
                if chart_df.empty:
                    st.info("No data exists for the selected period. Choose a wider range.")
                else:
                    st.plotly_chart(
                        line_chart(chart_df, "TIME_PERIOD", "OBS_VALUE", title="Average value over time"),
                        use_container_width=True,
                    )
            elif "OBS_VALUE" in df.columns:
                label_col = next((col for col in df.columns if col != "OBS_VALUE"), None)
                if label_col:
                    chart_df = df[[label_col, "OBS_VALUE"]].dropna(subset=["OBS_VALUE"]).head(30)
                    st.plotly_chart(bar_chart(chart_df, label_col, "OBS_VALUE"), use_container_width=True)

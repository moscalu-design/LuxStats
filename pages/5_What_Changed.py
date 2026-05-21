from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis.changes import (
    calculate_latest_change,
    calculate_top_decreases,
    calculate_top_increases,
    get_recently_updated_metrics,
)
from src.analysis.comparison import get_commune_comparison_metrics
from src.charts import ranked_bar_chart
from src.concepts import all_concepts
from src.data_access import get_dataset
from src.formatting import format_delta, format_value
from src.ui_components import (
    configure_page,
    download_csv,
    page_hero,
    render_sidebar,
    section_header,
)

configure_page("LuxStats - What Changed")
render_sidebar()

page_hero(
    "What Changed?",
    "The latest official figures, and the biggest recent moves",
    "Every number on this page is calculated from real cached data. Where the "
    "data does not support a calculation, the section says so — nothing is "
    "invented.",
)

# --------------------------------------------------------------------------
section_header("Latest moves in key statistics",
               "Most recent period compared with the one before it.")

change_rows = []
for concept in all_concepts():
    if not concept.popular:
        continue
    change = calculate_latest_change(concept.id)
    if change:
        change_rows.append(change)

if not change_rows:
    st.info(
        "No period-over-period changes can be calculated yet. Open a few "
        "charts (or the Dataset Explorer) so their data is cached, then revisit."
    )
else:
    for start in range(0, len(change_rows), 3):
        cols = st.columns(3)
        for col, change in zip(cols, change_rows[start:start + 3]):
            with col:
                fmt = change["value_format"]
                delta = format_delta(change["delta"], fmt)
                col.metric(
                    change["title"],
                    format_value(change["latest_value"], fmt),
                    delta=delta,
                    help=f"{change['previous_period']} → {change['latest_period']}",
                )
    st.caption("A positive change is not always good news — read each chart's "
               "explanation for context.")

st.divider()

# --------------------------------------------------------------------------
section_header("Recently updated data",
               "When each curated statistic was last refreshed from LUSTAT.")

updated = get_recently_updated_metrics()
freshness = pd.DataFrame(
    [
        {
            "Statistic": row["title"],
            "Topic": row["topic"],
            "Latest period": row["latest_period"] or "—",
            "Last refreshed": row["last_fetched"] or "Not cached yet",
        }
        for row in updated
    ]
)
st.dataframe(freshness, use_container_width=True, hide_index=True)
st.caption("‘Not cached yet’ means the dataset has not been downloaded locally "
           "on this deployment yet — open its chart to fetch it.")

st.divider()

# --------------------------------------------------------------------------
section_header("Fastest-changing communes",
               "Communes ranked by their most recent period-over-period change.")

commune_datasets = get_commune_comparison_metrics()
if not commune_datasets:
    st.info("No confirmed commune-level datasets are connected yet.")
else:
    dataset = st.selectbox(
        "Commune metric", commune_datasets,
        format_func=lambda d: f"{d.title} ({d.topic})",
    )
    try:
        with st.spinner("Loading official commune figures…"):
            raw = get_dataset(dataset.dataset_id)
        for column, expected in (dataset.default_filters or {}).items():
            if column in raw.columns:
                raw = raw[raw[column].astype(str) == str(expected)]
    except Exception as exc:  # noqa: BLE001
        raw = pd.DataFrame()
        st.warning("This commune dataset could not be loaded right now.")
        with st.expander("Advanced details"):
            st.code(str(exc))

    geo_col = dataset.geography_column or "GEO_LABEL"
    increases = calculate_top_increases(raw, geo_col, dataset.value_column,
                                        dataset.time_column)
    decreases = calculate_top_decreases(raw, geo_col, dataset.value_column,
                                        dataset.time_column)

    if increases.empty and decreases.empty:
        st.info(
            "This dataset does not have two comparable periods for communes "
            "yet, so a change ranking cannot be calculated."
        )
    else:
        left, right = st.columns(2)
        with left:
            st.markdown("**Biggest increases**")
            if increases.empty:
                st.caption("Not calculable for this dataset.")
            else:
                fig = ranked_bar_chart(increases, geo_col, "pct_change", top_n=10)
                fig.update_xaxes(title_text="% change", ticksuffix="%")
                fig.update_yaxes(title_text="")
                st.plotly_chart(fig, use_container_width=True)
        with right:
            st.markdown("**Biggest decreases**")
            if decreases.empty:
                st.caption("Not calculable for this dataset.")
            else:
                fig = ranked_bar_chart(decreases, geo_col, "pct_change", top_n=10)
                fig.update_xaxes(title_text="% change", ticksuffix="%")
                fig.update_yaxes(title_text="")
                st.plotly_chart(fig, use_container_width=True)
        combined = pd.concat([increases, decreases]).drop_duplicates()
        download_csv(combined, f"changes_{dataset.dataset_id}.csv",
                     "⬇︎ Download these changes (CSV)")

    with st.expander("Source details and caveats"):
        st.markdown(f"**Dataset ID:** `{dataset.dataset_id}`")
        st.markdown("**Source:** STATEC / LUSTAT")
        st.markdown(dataset.notes or "Official commune-level dataset.")

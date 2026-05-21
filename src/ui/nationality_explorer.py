"""Interactive nationality infographic for the Population topic page.

A plain-language breakdown of who lives in Luxembourg by nationality, with
a country selector so visitors can narrow down to one nationality. It is
fully deterministic — it only filters and charts official STATEC figures.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import line_chart, ranked_bar_chart, style_value_axis
from src.data.nationalities import (
    NATIONALITY_DATASET_ID,
    country_options,
    country_profile,
    load_nationality_frame,
    overview,
    top_nationalities,
)
from src.formatting import format_value
from src.ui_components import download_csv, section_header


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def _frame() -> pd.DataFrame:
    return load_nationality_frame()


def render_nationality_section() -> None:
    """Render the nationality overview and country explorer."""
    section_header(
        "Nationalities",
        "Luxembourg is one of the most international countries in the world. "
        "See which nationalities live here, and explore any single country.",
    )

    try:
        with st.spinner("Loading official nationality figures…"):
            df = _frame()
    except Exception:  # noqa: BLE001 - surface a friendly message
        st.warning("Nationality data could not be loaded right now. Please try again later.")
        return

    if df.empty:
        st.info("No nationality data is available right now.")
        return

    container = st.container(border=True)
    with container:
        meta = overview(df)
        cols = st.columns(4)
        cols[0].metric("Total residents", format_value(meta["total"], "number"))
        cols[1].metric("Luxembourgish", format_value(meta["luxembourgish"], "number"))
        cols[2].metric("Foreign residents", format_value(meta["foreign"], "number"))
        cols[3].metric("Foreign share", format_value(meta["pct_foreign"], "percent"))
        st.caption(
            f"Residents on 1 January {meta['year']}. Nearly half of Luxembourg's "
            "residents hold a foreign nationality."
        )

        top = top_nationalities(df, n=15)
        bar = ranked_bar_chart(
            top, "nationality", "value", top_n=15,
            title="The largest nationalities in Luxembourg",
        )
        bar.update_xaxes(title_text="")
        bar.update_yaxes(title_text="")
        bar.update_layout(showlegend=False)
        style_value_axis(bar, "number", axis="x")
        bar.update_traces(marker_color="#1f6f8b")
        st.plotly_chart(bar, use_container_width=True, key="nat_top_bar")

        st.markdown("##### Explore a nationality")
        options = country_options(df)
        if not options:
            st.info("No country-level nationality data is available right now.")
            return
        default = "Portugal" if "Portugal" in options else options[0]
        choice = st.selectbox(
            "Choose a country", options, index=options.index(default), key="nat_country",
        )

        profile = country_profile(df, choice)
        info = st.columns(3)
        info[0].metric(f"{choice} nationals", format_value(profile["latest"], "number"))
        info[1].metric("Share of all residents", format_value(profile["share"], "percent"))
        info[2].metric(
            "Rank among nationalities",
            f"{profile['rank']} of {profile['total_ranked']}" if profile["rank"] else "—",
        )

        trend = profile["trend"].rename(columns={"year": "Year", "value": "Residents"})
        if len(trend) > 1:
            line = line_chart(
                trend, x="Year", y="Residents",
                title=f"{choice} nationals living in Luxembourg",
            )
            line.update_xaxes(title_text="", dtick=2)
            line.update_yaxes(title_text="")
            style_value_axis(line, "number", axis="y")
            st.plotly_chart(line, use_container_width=True, key="nat_country_trend")
        else:
            st.caption("Not enough years of data to draw a trend for this nationality.")

        download_csv(trend, f"{choice}_residents.csv", "⬇︎ Download this data (CSV)")

        with st.expander("Source, units and notes"):
            st.caption(
                f"STATEC / LUSTAT dataset `{NATIONALITY_DATASET_ID}` — population by "
                "nationality in detail, residents of usual residence counted on "
                "1 January each year."
            )
            st.caption(
                "Continents and regional groupings are excluded from the country "
                "list. A few entries are historical (e.g. Soviet Union, Yugoslavia), "
                "and a small number of nationalities appear under more than one "
                "official code."
            )

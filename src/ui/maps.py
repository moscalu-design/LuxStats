"""Map view foundation for commune-level data.

The portal never fakes a map. If commune boundary GeoJSON is connected (see
:mod:`src.data.geography`), a real choropleth is drawn; otherwise a friendly,
honest empty state explains that boundaries are not connected yet.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.charts import PORTAL_COLORS
from src.data.geography import (
    COMMUNE_NAME_PROPERTY,
    commune_boundaries_available,
    geography_status,
    get_commune_geojson,
)


def map_supported() -> bool:
    """True when a commune-level map can actually be drawn."""
    return commune_boundaries_available()


def render_map_empty_state() -> None:
    """Render the honest 'no boundaries connected' message."""
    st.info(geography_status()["message"])


def render_commune_map(
    df: pd.DataFrame,
    *,
    name_col: str,
    value_col: str,
    title: str | None = None,
    key: str = "commune_map",
) -> bool:
    """Render a commune choropleth if boundaries are available.

    Returns True when a map was drawn, False when the empty state was shown
    instead. Never raises on missing data.
    """
    geojson = get_commune_geojson()
    if geojson is None:
        render_map_empty_state()
        return False
    if df is None or df.empty or name_col not in df.columns or value_col not in df.columns:
        st.info("There is no commune-level value to place on the map for this view.")
        return False
    try:
        fig = px.choropleth(
            df,
            geojson=geojson,
            locations=name_col,
            featureidkey=f"properties.{COMMUNE_NAME_PROPERTY}",
            color=value_col,
            color_continuous_scale=[[0, "#e8f0f4"], [1, PORTAL_COLORS[0]]],
            title=title,
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin=dict(l=0, r=0, t=40 if title else 0, b=0))
        st.plotly_chart(fig, use_container_width=True, key=key)
        return True
    except Exception:  # noqa: BLE001 - a broken map must not break the page
        render_map_empty_state()
        return False

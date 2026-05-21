"""Consistent source and data-freshness badges.

The user-facing badge is short and clean ("Official STATEC / LUSTAT data ·
Latest: 2024 · National"). All technical detail — dataset ID, columns, cache
timestamp — is tucked into an advanced expander, hidden by default.
"""

from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import streamlit as st

_LEVEL_LABELS = {
    "national": "National",
    "commune": "Commune-level",
    "region": "Regional",
    "canton": "Canton-level",
    "unknown": "Geography varies",
}


def _latest_period(metadata: dict[str, Any], df: pd.DataFrame | None) -> str | None:
    """Best-effort latest period: explicit metadata first, then the dataframe."""
    explicit = metadata.get("latest_period")
    if explicit:
        return str(explicit)
    if df is not None and not df.empty and "TIME_PERIOD" in df.columns:
        values = df["TIME_PERIOD"].dropna().astype(str)
        if not values.empty:
            return values.sort_values().iloc[-1]
    return None


def render_source_badge(metadata: dict[str, Any]) -> None:
    """Render the short, friendly source line."""
    level = _LEVEL_LABELS.get(str(metadata.get("geographic_level", "")).lower())
    bits = ["Official STATEC / LUSTAT data"]
    latest = metadata.get("latest_period")
    if latest:
        bits.append(f"Latest: {latest}")
    if level:
        bits.append(level)
    st.markdown(
        f"<div class='lux-source'>{escape(' · '.join(bits))}</div>",
        unsafe_allow_html=True,
    )


def render_freshness_badge(metadata: dict[str, Any], df: pd.DataFrame | None = None) -> None:
    """Render a compact freshness caption (latest period + cache timestamp)."""
    latest = _latest_period(metadata, df)
    fetched = metadata.get("last_fetched")
    bits = []
    if latest:
        bits.append(f"Latest period in the data: **{latest}**")
    if fetched:
        bits.append(f"Last refreshed: {fetched}")
    if not bits:
        bits.append("This statistic has not been cached locally yet.")
    st.caption(" · ".join(bits))


def render_source_expander(metadata: dict[str, Any], df: pd.DataFrame | None = None) -> None:
    """Render the advanced, technical source details inside an expander."""
    with st.expander("Source, units and advanced details", expanded=False):
        st.markdown(f"**Source:** {metadata.get('source', 'STATEC / LUSTAT')}")
        dataset_id = metadata.get("dataset_id")
        if dataset_id:
            st.markdown(f"**Official dataset ID:** `{dataset_id}`")
        if metadata.get("unit_note"):
            st.markdown(f"**What the numbers measure:** {metadata['unit_note']}")
        level = _LEVEL_LABELS.get(str(metadata.get("geographic_level", "")).lower())
        if level:
            st.markdown(f"**Geographic level:** {level}")
        latest = _latest_period(metadata, df)
        if latest:
            st.markdown(f"**Latest period in the data:** {latest}")
        if metadata.get("time_column"):
            st.markdown(f"**Time column:** `{metadata['time_column']}`")
        if metadata.get("value_column"):
            st.markdown(f"**Value column:** `{metadata['value_column']}`")
        if metadata.get("last_fetched"):
            st.markdown(f"**Cache timestamp:** {metadata['last_fetched']}")
        if metadata.get("row_count") is not None:
            st.markdown(f"**Rows in the full dataset:** {metadata['row_count']:,}")
        if metadata.get("caveat"):
            st.markdown(f"**Good to know:** {metadata['caveat']}")
        if metadata.get("notes"):
            st.markdown(f"**Technical notes:** {metadata['notes']}")

"""Reusable Streamlit period controls for charts."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from src.data.time_utils import (
    detect_frequency,
    filter_by_period_range,
    get_period_range_options,
    normalize_period_column,
)


@dataclass(frozen=True)
class TimeControlSelection:
    label: str
    start: int
    end: int
    frequency: str


def render_time_controls(
    df: pd.DataFrame,
    time_col: str,
    key_prefix: str,
    *,
    default: str = "Last 10 years",
) -> TimeControlSelection | None:
    """Render compact range controls and return the selected sort-key range."""
    if df.empty or time_col not in df.columns:
        return None
    normalized = normalize_period_column(df, time_col)
    if normalized.empty:
        return None
    options = get_period_range_options(normalized, time_col)
    if not options:
        return None
    labels = list(options)
    selected_default = default if default in options else "All"
    selected_label = st.segmented_control(
        "Time period",
        labels,
        default=selected_default,
        key=f"{key_prefix}_period_preset",
    )
    start, end = options[selected_label]
    frequency = detect_frequency(normalized[time_col])
    return TimeControlSelection(str(selected_label), int(start), int(end), frequency)


def apply_time_filter(df: pd.DataFrame, time_col: str, selection: TimeControlSelection | None) -> pd.DataFrame:
    if selection is None:
        return df.copy()
    return filter_by_period_range(df, time_col, selection.start, selection.end)

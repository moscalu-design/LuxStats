"""Robust period parsing and filtering helpers for STATEC-style time values."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd


_MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


@dataclass(frozen=True)
class ParsedPeriod:
    original: str
    frequency: str
    sort_key: int
    label: str
    year: int | None = None
    quarter: int | None = None
    month: int | None = None


def detect_time_column(df: pd.DataFrame, metadata: dict[str, Any] | None = None) -> str | None:
    if metadata and metadata.get("time_column") in df.columns:
        return str(metadata["time_column"])
    for column in ("TIME_PERIOD", "Year", "YEAR", "period", "Period", "date", "Date"):
        if column in df.columns:
            return column
    for column in df.columns:
        if "time" in column.lower() or "period" in column.lower() or "date" in column.lower():
            return column
    return None


def parse_period_value(value: Any) -> ParsedPeriod | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return ParsedPeriod(str(value), "daily", int(value.strftime("%Y%m%d")), value.strftime("%Y-%m-%d"), value.year, month=value.month)
    text = str(value).strip()
    if not text:
        return None

    match = re.fullmatch(r"(\d{4})", text)
    if match:
        year = int(match.group(1))
        return ParsedPeriod(text, "annual", year * 10000, str(year), year)

    match = re.fullmatch(r"(\d{4})[-\s]?[QT](\d)", text, flags=re.IGNORECASE)
    if match:
        year, quarter = int(match.group(1)), int(match.group(2))
        if 1 <= quarter <= 4:
            return ParsedPeriod(text, "quarterly", year * 100 + quarter, f"{year} Q{quarter}", year, quarter=quarter)

    match = re.fullmatch(r"(\d{4})[-\s]?M?(\d{2})", text, flags=re.IGNORECASE)
    if match:
        year, month = int(match.group(1)), int(match.group(2))
        if 1 <= month <= 12:
            return ParsedPeriod(text, "monthly", year * 100 + month, f"{year}-{month:02d}", year, month=month)

    match = re.fullmatch(r"([A-Za-z]{3,9})\s+(\d{4})", text)
    if match:
        month = _MONTHS.get(match.group(1).lower())
        year = int(match.group(2))
        if month:
            return ParsedPeriod(text, "monthly", year * 100 + month, f"{year}-{month:02d}", year, month=month)

    parsed = pd.to_datetime(text, errors="coerce")
    if not pd.isna(parsed):
        return ParsedPeriod(text, "daily", int(parsed.strftime("%Y%m%d")), parsed.strftime("%Y-%m-%d"), parsed.year, month=parsed.month)
    return None


def normalize_period_column(df: pd.DataFrame, time_col: str) -> pd.DataFrame:
    out = df.copy()
    if out.empty or time_col not in out.columns:
        out["_period_sort"] = pd.Series(dtype="int")
        out["_period_label"] = pd.Series(dtype="str")
        out["_period_frequency"] = pd.Series(dtype="str")
        return out
    parsed = out[time_col].map(parse_period_value)
    out["_period_sort"] = parsed.map(lambda item: item.sort_key if item else pd.NA)
    out["_period_label"] = parsed.map(lambda item: item.label if item else "")
    out["_period_frequency"] = parsed.map(lambda item: item.frequency if item else "unknown")
    return out.dropna(subset=["_period_sort"]).copy()


def detect_frequency(series: pd.Series) -> str:
    parsed = [parse_period_value(value) for value in series.dropna().head(200)]
    freqs = [item.frequency for item in parsed if item]
    if not freqs:
        return "unknown"
    return pd.Series(freqs).mode().iloc[0]


def get_latest_period(df: pd.DataFrame, time_col: str) -> str | None:
    work = normalize_period_column(df, time_col)
    if work.empty:
        return None
    latest = work.sort_values("_period_sort").iloc[-1]
    return str(latest[time_col])


def get_previous_period(df: pd.DataFrame, time_col: str) -> str | None:
    work = normalize_period_column(df, time_col)
    if work.empty:
        return None
    periods = work[[time_col, "_period_sort"]].drop_duplicates().sort_values("_period_sort")
    if len(periods) < 2:
        return None
    return str(periods.iloc[-2][time_col])


def get_period_range_options(df: pd.DataFrame, time_col: str) -> dict[str, tuple[int, int]]:
    work = normalize_period_column(df, time_col)
    if work.empty:
        return {}
    lo, hi = int(work["_period_sort"].min()), int(work["_period_sort"].max())
    frequency = detect_frequency(work[time_col])
    options = {"All": (lo, hi)}
    if frequency == "annual":
        latest_year = hi // 10000
        options["Last 5 years"] = (max(lo, (latest_year - 4) * 10000), hi)
        options["Last 10 years"] = (max(lo, (latest_year - 9) * 10000), hi)
        options["Since 2000"] = (max(lo, 2000 * 10000), hi)
    elif frequency in {"quarterly", "monthly"}:
        # sort keys are YYYYQ or YYYYMM, so use a generous year cutoff.
        latest_year = hi // 100
        options["Last 5 years"] = (max(lo, (latest_year - 4) * 100), hi)
        options["Last 10 years"] = (max(lo, (latest_year - 9) * 100), hi)
        options["Since 2000"] = (max(lo, 2000 * 100), hi)
    return options


def filter_by_period_range(df: pd.DataFrame, time_col: str, start: int, end: int) -> pd.DataFrame:
    work = normalize_period_column(df, time_col)
    if work.empty:
        return work
    return work[(work["_period_sort"] >= start) & (work["_period_sort"] <= end)].copy()


def calculate_period_change(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    time_col: str,
) -> pd.DataFrame:
    empty = pd.DataFrame(columns=[group_col, "previous", "latest", "change", "pct_change"])
    if df.empty or any(col not in df.columns for col in (group_col, value_col, time_col)):
        return empty
    work = normalize_period_column(df, time_col)
    if work.empty:
        return empty
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    periods = work[["_period_sort", time_col]].drop_duplicates().sort_values("_period_sort")
    if len(periods) < 2:
        return empty
    latest_key = periods.iloc[-1]["_period_sort"]
    prev_key = periods.iloc[-2]["_period_sort"]
    latest = work[work["_period_sort"] == latest_key].groupby(group_col)[value_col].mean()
    previous = work[work["_period_sort"] == prev_key].groupby(group_col)[value_col].mean()
    out = pd.concat({"latest": latest, "previous": previous}, axis=1).dropna()
    if out.empty:
        return empty
    out["change"] = out["latest"] - out["previous"]
    out["pct_change"] = out["change"] / out["previous"].replace(0, pd.NA) * 100
    return out.reset_index()

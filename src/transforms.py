"""Common dataframe transformations for dashboards."""

from __future__ import annotations

import pandas as pd


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(col).strip().replace(" ", "_") for col in out.columns]
    if "OBS_VALUE" in out.columns:
        out["OBS_VALUE"] = pd.to_numeric(out["OBS_VALUE"], errors="coerce")
    if "TIME_PERIOD" in out.columns:
        out["TIME_PERIOD"] = out["TIME_PERIOD"].astype(str)
    return out


def time_series(df: pd.DataFrame, value_col: str = "OBS_VALUE", time_col: str = "TIME_PERIOD") -> pd.DataFrame:
    if df.empty or time_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame(columns=[time_col, value_col])
    return (
        df[[time_col, value_col]]
        .dropna(subset=[value_col])
        .groupby(time_col, as_index=False)[value_col]
        .mean()
        .sort_values(time_col)
    )


def ranking_by_latest(
    df: pd.DataFrame,
    label_col: str,
    value_col: str = "OBS_VALUE",
    time_col: str = "TIME_PERIOD",
    top_n: int = 20,
) -> pd.DataFrame:
    if df.empty or label_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame(columns=[label_col, value_col])
    work = df.copy()
    if time_col in work.columns and not work[time_col].dropna().empty:
        latest = work[time_col].dropna().astype(str).sort_values().iloc[-1]
        work = work[work[time_col].astype(str) == latest]
    return (
        work[[label_col, value_col]]
        .dropna(subset=[value_col])
        .groupby(label_col, as_index=False)[value_col]
        .mean()
        .sort_values(value_col, ascending=False)
        .head(top_n)
    )


def grouped_comparison(df: pd.DataFrame, group_col: str, value_col: str = "OBS_VALUE") -> pd.DataFrame:
    if df.empty or group_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame(columns=[group_col, value_col])
    return (
        df[[group_col, value_col]]
        .dropna(subset=[value_col])
        .groupby(group_col, as_index=False)[value_col]
        .mean()
        .sort_values(value_col, ascending=False)
    )


def index_rebase(
    df: pd.DataFrame,
    value_col: str = "OBS_VALUE",
    time_col: str = "TIME_PERIOD",
    base_period: str | None = None,
) -> pd.DataFrame:
    out = df.copy()
    if out.empty or value_col not in out.columns or time_col not in out.columns:
        out["INDEX_VALUE"] = pd.Series(dtype="float")
        return out
    sorted_periods = out[time_col].dropna().astype(str).sort_values()
    base = base_period or (sorted_periods.iloc[0] if not sorted_periods.empty else None)
    if base is None:
        out["INDEX_VALUE"] = pd.NA
        return out
    base_values = out.loc[out[time_col].astype(str) == str(base), value_col].dropna()
    base_value = base_values.mean() if not base_values.empty else None
    out["INDEX_VALUE"] = (out[value_col] / base_value * 100) if base_value else pd.NA
    return out


def year_over_year_growth(
    df: pd.DataFrame,
    value_col: str = "OBS_VALUE",
    time_col: str = "TIME_PERIOD",
) -> pd.DataFrame:
    out = time_series(df, value_col=value_col, time_col=time_col)
    if out.empty:
        out["YOY_GROWTH"] = pd.Series(dtype="float")
        return out
    out["YOY_GROWTH"] = out[value_col].pct_change() * 100
    return out

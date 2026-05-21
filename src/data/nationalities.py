"""Nationality breakdown of Luxembourg's resident population.

Backed by the confirmed LUSTAT dataset ``DF_B1113`` ("Population by
nationalities in detail on 1st January"). The dataset mixes individual
nationalities with aggregates (continents, "Total foreigners", regional
groupings); the helpers here separate real nationalities from those
aggregates deterministically, using the stable SDMX codes.
"""

from __future__ import annotations

import pandas as pd

from src.data_access import get_dataset
from src.transforms import normalize_columns

NATIONALITY_DATASET_ID = "DF_B1113"

_TOTAL_CODE = "L01"        # TOTAL POPULATION
_LUX_CODE = "SL001"        # Luxembourg (Luxembourgish nationals)
_FOREIGN_CODE = "SL002"    # Total foreigners

# Codes that are aggregates or regional groupings rather than a single
# nationality: continents (L02-L08), the total, the foreign total, and the
# "Other ..." / continental sub-region buckets.
_NON_COUNTRY_CODES = {
    "L01", "L02", "L03", "L04", "L05", "L06", "L07", "L08",
    "SL001", "SL002", "SL003", "SL004", "SL058", "SL059", "SL060",
}


def load_nationality_frame() -> pd.DataFrame:
    """Return a tidy frame with columns ``code``, ``nationality``, ``year``, ``value``."""
    empty = pd.DataFrame(columns=["code", "nationality", "year", "value"])
    raw = normalize_columns(get_dataset(NATIONALITY_DATASET_ID))
    if raw.empty or "OBS_VALUE" not in raw.columns or "POPULATION" not in raw.columns:
        return empty
    df = raw.copy()
    if "POPULATION_LABEL" in df.columns:
        df = df.rename(columns={"POPULATION": "code", "POPULATION_LABEL": "nationality"})
    else:
        df["code"] = df["POPULATION"]
        df["nationality"] = df["POPULATION"]
    df["value"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df["year"] = df["TIME_PERIOD"].astype(str).str[:4]
    df = df[df["year"].str.fullmatch(r"\d{4}")]
    if df.empty:
        return empty
    df["year"] = df["year"].astype(int)
    df = df.dropna(subset=["value"])
    return df[["code", "nationality", "year", "value"]].reset_index(drop=True)


def latest_year(df: pd.DataFrame) -> int:
    return int(df["year"].max())


def overview(df: pd.DataFrame) -> dict:
    """Headline figures for the most recent year: total, Luxembourgish, foreign."""
    year = latest_year(df)
    current = df[df["year"] == year]

    def _value(code: str) -> float | None:
        match = current.loc[current["code"] == code, "value"]
        return float(match.iloc[0]) if not match.empty else None

    total = _value(_TOTAL_CODE)
    luxembourgish = _value(_LUX_CODE)
    foreign = _value(_FOREIGN_CODE)
    pct_foreign = (foreign / total * 100) if total and foreign else None
    return {
        "year": year,
        "total": total,
        "luxembourgish": luxembourgish,
        "foreign": foreign,
        "pct_foreign": pct_foreign,
    }


def _ranked_nationalities(current: pd.DataFrame) -> pd.DataFrame:
    """Countries plus Luxembourg for one year, summed by name and ranked."""
    keep = current[~current["code"].isin(_NON_COUNTRY_CODES) | (current["code"] == _LUX_CODE)]
    ranked = keep.groupby("nationality", as_index=False)["value"].sum()
    return ranked.sort_values("value", ascending=False).reset_index(drop=True)


def top_nationalities(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """The ``n`` largest nationalities (including Luxembourgish) in the latest year."""
    current = df[df["year"] == latest_year(df)]
    return _ranked_nationalities(current).head(n)


def country_options(df: pd.DataFrame) -> list[str]:
    """Selectable nationalities — individual countries present in the latest year."""
    year = latest_year(df)
    current = df[(df["year"] == year) & (df["value"] > 0)]
    countries = current[~current["code"].isin(_NON_COUNTRY_CODES)]
    return sorted(countries["nationality"].unique().tolist())


def country_profile(df: pd.DataFrame, nationality: str) -> dict:
    """Latest count, population share, rank and full trend for one nationality."""
    year = latest_year(df)
    current = df[df["year"] == year]
    latest = float(current.loc[current["nationality"] == nationality, "value"].sum())

    total_match = current.loc[current["code"] == _TOTAL_CODE, "value"]
    total = float(total_match.iloc[0]) if not total_match.empty else None
    share = (latest / total * 100) if total else None

    ranked = _ranked_nationalities(current)
    rank_idx = ranked.index[ranked["nationality"] == nationality]
    rank = int(rank_idx[0] + 1) if len(rank_idx) else None

    trend = (
        df[df["nationality"] == nationality]
        .groupby("year", as_index=False)["value"].sum()
        .sort_values("year")
        .reset_index(drop=True)
    )
    return {
        "year": year,
        "latest": latest,
        "share": share,
        "rank": rank,
        "total_ranked": int(len(ranked)),
        "trend": trend,
    }

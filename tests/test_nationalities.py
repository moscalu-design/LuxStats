"""Tests for the nationality breakdown helpers (deterministic, no network)."""

from __future__ import annotations

import pandas as pd

from src.data.nationalities import (
    country_options,
    country_profile,
    overview,
    top_nationalities,
)


def _frame() -> pd.DataFrame:
    """Synthetic frame shaped like load_nationality_frame()'s output."""
    rows: list[tuple[str, str, int, float]] = []
    for year in (2024, 2025):
        rows += [
            ("L01", "TOTAL POPULATION", year, 1000.0),
            ("SL001", "Luxembourg", year, 600.0),
            ("SL002", "Total foreigners", year, 400.0),
            ("L02", "EUROPE", year, 300.0),
            ("SSL21", "Portugal", year, 150.0),
            ("SSL11", "France", year, 90.0),
            ("SSL15", "Italy", year, 40.0),
        ]
    return pd.DataFrame(rows, columns=["code", "nationality", "year", "value"])


def test_overview_uses_latest_year_totals() -> None:
    meta = overview(_frame())
    assert meta["year"] == 2025
    assert meta["total"] == 1000.0
    assert meta["luxembourgish"] == 600.0
    assert meta["foreign"] == 400.0
    assert meta["pct_foreign"] == 40.0


def test_top_nationalities_excludes_aggregates_keeps_luxembourg() -> None:
    top = top_nationalities(_frame(), n=15)
    names = top["nationality"].tolist()
    assert names == ["Luxembourg", "Portugal", "France", "Italy"]
    # Continent and total aggregates must never appear.
    assert "EUROPE" not in names
    assert "TOTAL POPULATION" not in names
    assert "Total foreigners" not in names


def test_country_options_lists_only_individual_countries() -> None:
    options = country_options(_frame())
    assert options == ["France", "Italy", "Portugal"]


def test_country_profile_reports_share_and_rank() -> None:
    profile = country_profile(_frame(), "Portugal")
    assert profile["latest"] == 150.0
    assert profile["share"] == 15.0
    # Luxembourg (600) ranks first, Portugal (150) second.
    assert profile["rank"] == 2
    assert profile["total_ranked"] == 4
    assert len(profile["trend"]) == 2

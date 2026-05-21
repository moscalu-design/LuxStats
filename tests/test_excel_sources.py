from __future__ import annotations

import pandas as pd
import pytest

from src.data.excel_sources import (
    AVERAGE_PRICES_ID,
    HOUSE_PRICE_INDEX_ID,
    _parse_quarter,
    _parse_quarterly_block,
    _parse_year,
    get_excel_dataset,
    is_excel_dataset,
)


class _FakeSheet:
    """Minimal xlrd-sheet stand-in for offline parser tests."""

    def __init__(self, rows: list[list[object]]):
        self._rows = rows
        self.nrows = len(rows)
        self.ncols = max((len(r) for r in rows), default=0)

    def cell_value(self, r: int, c: int) -> object:
        row = self._rows[r]
        return row[c] if c < len(row) else ""


def test_is_excel_dataset_routing() -> None:
    assert is_excel_dataset(HOUSE_PRICE_INDEX_ID)
    assert is_excel_dataset(AVERAGE_PRICES_ID)
    assert not is_excel_dataset("DF_X021")


def test_parse_year_and_quarter() -> None:
    assert _parse_year(2018.0) == 2018
    assert _parse_year("2021.0") == 2021
    assert _parse_year("") is None
    assert _parse_quarter("Q1") == "Q1"
    assert _parse_quarter("Q4 ") == "Q4"
    assert _parse_quarter("T3 3") == "Q3"
    assert _parse_quarter("") is None


def test_parse_quarterly_block_offline() -> None:
    rows = [
        ["intro"],
        ["Year", "Quarter", "Index", "Q%", "Index", "Q%"],
        [2020, "Q1", 100.0, 1.0, 200.0, 2.0],
        ["", "Q2", 110.0, 1.0, 210.0, 2.0],
        [2021, "Q1", 120.0, 1.0, 220.0, 2.0],
        ["Year", "", "annual section starts here"],
        [2020, "", 105.0],
    ]
    df = _parse_quarterly_block(_FakeSheet(rows), {2: "Index A", 4: "Index B"})
    assert set(df.columns) == {"TIME_PERIOD", "OBS_VALUE", "SPECIFICATION"}
    # Two quarters x two series, annual block excluded.
    assert len(df) == 6
    assert set(df["TIME_PERIOD"]) == {"2020-Q1", "2020-Q2", "2021-Q1"}
    a_q1 = df[(df["SPECIFICATION"] == "Index A") & (df["TIME_PERIOD"] == "2020-Q1")]
    assert a_q1["OBS_VALUE"].iloc[0] == 100.0


def test_parse_quarterly_block_handles_missing_header() -> None:
    df = _parse_quarterly_block(_FakeSheet([["no", "header", "here"]]), {2: "X"})
    assert df.empty
    assert list(df.columns) == ["TIME_PERIOD", "OBS_VALUE", "SPECIFICATION"]


@pytest.mark.parametrize("dataset_id", [HOUSE_PRICE_INDEX_ID, AVERAGE_PRICES_ID])
def test_get_excel_dataset_when_reachable(dataset_id: str) -> None:
    """Network-tolerant: assert structure when the STATEC file is reachable."""
    try:
        df = get_excel_dataset(dataset_id)
    except Exception:  # noqa: BLE001 - offline / STATEC unavailable
        pytest.skip("STATEC D4011 workbook is not reachable in this environment.")
    assert not df.empty
    assert {"TIME_PERIOD", "OBS_VALUE", "SPECIFICATION"}.issubset(df.columns)
    assert pd.api.types.is_numeric_dtype(df["OBS_VALUE"])
    assert df["TIME_PERIOD"].str.fullmatch(r"\d{4}-Q[1-4]").all()

"""STATEC publication Excel files as curated datasets.

Some headline statistics — notably housing **sale prices** — are published by
STATEC as Excel workbooks in the "Logement en chiffres" series rather than
through the LUSTAT SDMX API. This module downloads and parses those workbooks
into the same tidy ``TIME_PERIOD / OBS_VALUE / SPECIFICATION`` shape the rest
of the portal expects, so a normal :class:`~src.concepts.Concept` can chart
them with no special-casing downstream.

Source publication:
https://statistiques.public.lu/en/publications/series/logement-chiffres.html
Data file: D4011 — Acquisition prices for dwellings (quarterly).
"""

from __future__ import annotations

import re
import time
from functools import lru_cache
from pathlib import Path

import pandas as pd
import requests

from src.config import CACHE_DIR

# Dataset IDs. The ``STATEC_XLS_`` prefix is what data_access uses to route a
# request here instead of to the LUSTAT SDMX API.
EXCEL_ID_PREFIX = "STATEC_XLS_"
HOUSE_PRICE_INDEX_ID = "STATEC_XLS_HOUSE_PRICE_INDEX"
AVERAGE_PRICES_ID = "STATEC_XLS_AVERAGE_PRICES"
TOURISM_ACTIVITY_ID = "STATEC_XLS_TOURISM_ACTIVITY_D5310"

D4011_URL = (
    "https://statistiques.public.lu/dam-assets/fr/donnees-autres-formats/"
    "indicateurs-court-terme/economie-totale-prix/D4011.xls"
)
D4011_PATH = CACHE_DIR / "statec" / "D4011.xls"
D5310_URL = (
    "https://statistiques.public.lu/dam-assets/fr/donnees-autres-formats/"
    "indicateurs-court-terme/entreprises/D5310.xlsx"
)
D5310_PATH = CACHE_DIR / "statec" / "D5310.xlsx"
DOWNLOAD_TTL_SECONDS = 7 * 24 * 3600

# Series offered by each dataset: column index in the workbook -> friendly name.
_HOUSE_PRICE_SERIES = {
    2: "All dwellings",
    5: "Existing dwellings",
    8: "Existing houses",
    11: "Existing apartments",
    14: "New dwellings",
}
# The "average prices" sheet covers apartments only (houses are not split out).
_AVERAGE_PRICE_SERIES = {
    2: "All apartments",
    5: "Existing apartments",
    8: "New apartments",
}


def is_excel_dataset(dataset_id: str) -> bool:
    """True when a dataset id should be served from a STATEC Excel file."""
    return str(dataset_id).startswith(EXCEL_ID_PREFIX)


# --------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------

def _download_d4011(force_refresh: bool = False) -> Path:
    """Ensure the D4011 workbook is cached locally; return its path."""
    D4011_PATH.parent.mkdir(parents=True, exist_ok=True)
    fresh = (
        D4011_PATH.exists()
        and D4011_PATH.stat().st_size > 0
        and time.time() - D4011_PATH.stat().st_mtime < DOWNLOAD_TTL_SECONDS
    )
    if fresh and not force_refresh:
        return D4011_PATH
    resp = requests.get(
        D4011_URL,
        headers={"User-Agent": "Mozilla/5.0 (LuxStats statistics portal)"},
        timeout=60,
    )
    resp.raise_for_status()
    D4011_PATH.write_bytes(resp.content)
    return D4011_PATH


def _download_d5310(force_refresh: bool = False) -> Path:
    """Ensure the D5310 tourism workbook is cached locally; return its path."""
    D5310_PATH.parent.mkdir(parents=True, exist_ok=True)
    fresh = (
        D5310_PATH.exists()
        and D5310_PATH.stat().st_size > 0
        and time.time() - D5310_PATH.stat().st_mtime < DOWNLOAD_TTL_SECONDS
    )
    if fresh and not force_refresh:
        return D5310_PATH
    resp = requests.get(
        D5310_URL,
        headers={"User-Agent": "Mozilla/5.0 (LuxStats statistics portal)"},
        timeout=60,
    )
    resp.raise_for_status()
    D5310_PATH.write_bytes(resp.content)
    return D5310_PATH


# --------------------------------------------------------------------------
# Parsing helpers
# --------------------------------------------------------------------------

def _parse_year(value: object) -> int | None:
    try:
        year = int(float(value))
    except (ValueError, TypeError):
        return None
    return year if 1900 < year < 2100 else None


def _parse_quarter(value: object) -> str | None:
    match = re.search(r"[1-4]", str(value or ""))
    return f"Q{match.group()}" if match else None


def _header_rows(sheet) -> list[int]:
    """Row indices whose first cell is the literal label 'Year'."""
    rows = []
    for r in range(sheet.nrows):
        if str(sheet.cell_value(r, 0)).strip().lower() == "year":
            rows.append(r)
    return rows


def _parse_quarterly_block(sheet, series: dict[int, str]) -> pd.DataFrame:
    """Parse the quarterly section of a D4011 sheet into a tidy frame.

    The quarterly block starts at the header row whose first two cells are
    'Year' and 'Quarter', and ends where the annual block ('Year' only) begins.
    """
    empty = pd.DataFrame(columns=["TIME_PERIOD", "OBS_VALUE", "SPECIFICATION"])
    headers = _header_rows(sheet)
    quarterly_header = next(
        (r for r in headers
         if str(sheet.cell_value(r, 1)).strip().lower() == "quarter"),
        None,
    )
    if quarterly_header is None:
        return empty
    annual_header = next((r for r in headers if r > quarterly_header), sheet.nrows)

    records: list[dict[str, object]] = []
    current_year: int | None = None
    for r in range(quarterly_header + 1, annual_header):
        year = _parse_year(sheet.cell_value(r, 0))
        if year is not None:
            current_year = year
        quarter = _parse_quarter(sheet.cell_value(r, 1))
        if current_year is None or quarter is None:
            continue
        period = f"{current_year}-{quarter}"
        for col, name in series.items():
            if col >= sheet.ncols:
                continue
            raw = sheet.cell_value(r, col)
            value = pd.to_numeric(raw, errors="coerce")
            if pd.isna(value):
                continue
            records.append(
                {"TIME_PERIOD": period, "OBS_VALUE": float(value),
                 "SPECIFICATION": name}
            )
    if not records:
        return empty
    return pd.DataFrame.from_records(records)


@lru_cache(maxsize=8)
def _parse_dataset(dataset_id: str, path_key: str) -> pd.DataFrame:
    """Parse one Excel-backed dataset (cached by file path + mtime)."""
    if dataset_id == TOURISM_ACTIVITY_ID:
        return _parse_tourism_activity()

    import xlrd  # imported lazily so the rest of the app never needs it

    book = xlrd.open_workbook(D4011_PATH)
    if dataset_id == HOUSE_PRICE_INDEX_ID:
        return _parse_quarterly_block(
            book.sheet_by_name("EN house price index"), _HOUSE_PRICE_SERIES
        )
    if dataset_id == AVERAGE_PRICES_ID:
        return _parse_quarterly_block(
            book.sheet_by_name("EN average prices"), _AVERAGE_PRICE_SERIES
        )
    raise ValueError(f"Unknown Excel dataset id: {dataset_id}")


def _parse_tourism_sheet(path: Path, sheet_name: str, indicator: str) -> pd.DataFrame:
    """Parse one D5310 English sheet into monthly tidy rows."""
    wide = pd.read_excel(path, sheet_name=sheet_name, dtype=str)
    if wide.shape[1] < 3:
        return pd.DataFrame(columns=["TIME_PERIOD", "OBS_VALUE", "SPECIFICATION"])

    region_col = str(wide.columns[0])
    type_col = str(wide.columns[1])
    month_cols = [col for col in wide.columns[2:] if re.fullmatch(r"\d{4}\.\d{2}", str(col))]
    if not month_cols:
        return pd.DataFrame(columns=["TIME_PERIOD", "OBS_VALUE", "SPECIFICATION"])

    tidy = wide.melt(
        id_vars=[region_col, type_col],
        value_vars=month_cols,
        var_name="TIME_PERIOD",
        value_name="OBS_VALUE",
    )
    tidy["OBS_VALUE"] = pd.to_numeric(tidy["OBS_VALUE"], errors="coerce")
    tidy = tidy.dropna(subset=["OBS_VALUE"])
    tidy["TIME_PERIOD"] = tidy["TIME_PERIOD"].astype(str).str.replace(".", "-", regex=False)
    tidy["SPECIFICATION"] = indicator
    tidy["REGION"] = tidy[region_col]
    tidy["ACCOMMODATION_TYPE"] = tidy[type_col]
    return tidy[["TIME_PERIOD", "OBS_VALUE", "SPECIFICATION", "REGION", "ACCOMMODATION_TYPE"]]


def _parse_tourism_activity() -> pd.DataFrame:
    """Parse D5310 arrivals and overnight stays from reviewed English sheets."""
    frames = [
        _parse_tourism_sheet(D5310_PATH, "arrivals", "Arrivals"),
        _parse_tourism_sheet(D5310_PATH, "overnight stays", "Overnight stays"),
    ]
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return pd.DataFrame(columns=["TIME_PERIOD", "OBS_VALUE", "SPECIFICATION"])
    return pd.concat(frames, ignore_index=True)


def get_excel_dataset(dataset_id: str, refresh: bool = False) -> pd.DataFrame:
    """Return a tidy TIME_PERIOD/OBS_VALUE/SPECIFICATION frame for a STATEC
    Excel-backed dataset. Raises on download or parsing failure so callers can
    show a friendly error state."""
    if not is_excel_dataset(dataset_id):
        raise ValueError(f"{dataset_id} is not a STATEC Excel dataset.")
    path = _download_d5310(force_refresh=refresh) if dataset_id == TOURISM_ACTIVITY_ID else _download_d4011(force_refresh=refresh)
    # path mtime is part of the cache key so a refreshed file is re-parsed.
    return _parse_dataset(dataset_id, f"{path}:{path.stat().st_mtime_ns}").copy()

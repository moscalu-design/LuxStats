from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.file_ingestion import (
    INGESTION_STATES,
    cached_file_path,
    inspect_excel_file,
    list_excel_sheets,
    normalize_excel_table,
    preview_excel_sheet,
    safe_read_excel,
)


def test_safe_read_excel_handles_missing_file() -> None:
    df = safe_read_excel("/nonexistent/file.xlsx")
    assert df.empty


def test_inspect_missing_file_reports_failed() -> None:
    info = inspect_excel_file("/nonexistent/file.xlsx")
    assert info["status"] == "failed"
    assert info["sheet_count"] == 0


def test_list_sheets_missing_file_is_empty() -> None:
    assert list_excel_sheets("/nonexistent/file.xls") == []


def test_normalize_excel_table_drops_empty() -> None:
    df = pd.DataFrame({"A": [1, None], "B": [None, None]})
    cleaned = normalize_excel_table(df)
    assert "B" not in cleaned.columns
    assert len(cleaned) == 1


def test_inspect_real_workbook(tmp_path: Path) -> None:
    """A workbook with a time + value column should be flagged importable."""
    path = tmp_path / "sample.xlsx"
    pd.DataFrame(
        {
            "Year": [2020, 2021, 2022],
            "Commune": ["Luxembourg", "Hesperange", "Esch-sur-Alzette"],
            "Value": [10.0, 20.0, 30.0],
        }
    ).to_excel(path, index=False)

    info = inspect_excel_file(path)
    assert info["status"] in INGESTION_STATES
    assert info["sheet_count"] == 1
    sheet = info["sheets"][0]
    assert "Year" in sheet["likely_time_columns"]
    assert "Value" in sheet["likely_value_columns"]
    assert sheet["detected_communes"]  # commune names were recognized
    assert info["status"] == "importable"

    preview = preview_excel_sheet(path)
    assert not preview.empty


def test_cached_file_path_is_sanitized() -> None:
    path = cached_file_path({"file_url": "https://statistiques.public.lu/x/D4011.xls"})
    assert path.name == "D4011.xls"

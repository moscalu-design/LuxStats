from __future__ import annotations

from src.catalog import search_catalog


def test_catalog_aliases_find_housing_prices() -> None:
    result = search_catalog("real estate")
    assert "Housing" in result["theme"].tolist()


def test_catalog_aliases_find_salary() -> None:
    result = search_catalog("pay sector")
    assert "Salaries" in result["theme"].tolist()


def test_catalog_covers_secondary_portal_themes() -> None:
    result = search_catalog("budget")
    assert "Public Finance" in result["theme"].tolist()

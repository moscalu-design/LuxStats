from __future__ import annotations

from src.catalog import catalog_dataframe, catalog_validation_issues, is_placeholder_dataset_id, search_catalog
from src.dashboard_specs import DASHBOARD_SPECS


def test_catalog_aliases_find_housing_prices() -> None:
    result = search_catalog("real estate")
    assert "Housing" in result["theme"].tolist()


def test_catalog_aliases_find_salary() -> None:
    result = search_catalog("pay sector")
    assert "Salaries" in result["theme"].tolist()


def test_catalog_covers_secondary_portal_themes() -> None:
    result = search_catalog("budget")
    assert "Public Finance" in result["theme"].tolist()


def test_catalog_metadata_is_internally_consistent() -> None:
    assert catalog_validation_issues() == []


def test_unconfirmed_catalog_entries_use_todo_confirm_prefix() -> None:
    result = search_catalog()
    unconfirmed = result[result["status"] == "needs_confirmation"]
    assert not unconfirmed.empty
    assert unconfirmed["dataset_id"].map(is_placeholder_dataset_id).all()


def test_dashboard_specs_have_catalog_entries() -> None:
    for theme in DASHBOARD_SPECS:
        assert not search_catalog(theme=theme).empty


def test_catalog_exposes_commune_portal_metadata() -> None:
    df = catalog_dataframe()
    required = {
        "geographic_level",
        "geography_column",
        "commune_code_column",
        "commune_name_column",
        "value_column",
        "time_column",
        "commune_portal",
    }
    assert required.issubset(df.columns)
    commune_entries = df[df["commune_portal"]]
    assert not commune_entries.empty
    assert set(commune_entries["geographic_level"]) == {"commune"}

from __future__ import annotations

from src.data.source_catalog import (
    REQUIRED_FIELDS,
    SOURCE_TYPES,
    assign_priority,
    build_unified_source_catalog,
    catalog_summary,
    catalog_validation_issues,
    load_unified_source_catalog,
    search_source_catalog,
)
from src.reports.source_catalog_report import generate_report


def _record(**overrides) -> dict:
    base = {
        "source_id": "api:DF_TEST",
        "source_type": "LUSTAT_API",
        "title": "Test dataset",
        "description": "",
        "category": "Population",
        "keywords": ["population", "test"],
        "geographic_level": "national",
        "file_type": "",
        "publication_family": "",
    }
    base.update(overrides)
    return base


def test_assign_priority_high_for_commune_housing() -> None:
    result = assign_priority(_record(category="Housing", geographic_level="commune",
                                     source_type="STATEC_EXCEL", file_type="xlsx"))
    assert result["priority"] == "high"
    assert result["priority_score"] >= 5
    assert result["priority_reason"]


def test_assign_priority_low_for_pdf_unknown() -> None:
    result = assign_priority(_record(category="Other / Unknown",
                                     source_type="PUBLICATION_PDF", file_type="pdf"))
    assert result["priority"] == "low"


def test_search_filters_and_text() -> None:
    records = [
        _record(source_id="a", title="Housing prices", category="Housing"),
        _record(source_id="b", title="Salary by sector", category="Salaries / Income"),
        _record(source_id="c", title="Population growth", category="Population"),
    ]
    by_text = search_source_catalog("housing", records=records)
    assert [r["source_id"] for r in by_text] == ["a"]
    by_filter = search_source_catalog("", {"category": "Population"}, records=records)
    assert [r["source_id"] for r in by_filter] == ["c"]


def test_validation_flags_missing_fields_and_duplicates() -> None:
    bad = [
        {"source_id": "x", "source_type": "LUSTAT_API", "title": "", "category": "Population"},
        {"source_id": "x", "source_type": "LUSTAT_API", "title": "Dup", "category": "Population"},
    ]
    issues = catalog_validation_issues(bad)
    assert any("missing required field" in i for i in issues)
    assert any("Duplicate source_id" in i for i in issues)


def test_required_fields_and_source_types_constants() -> None:
    assert set(REQUIRED_FIELDS) == {"source_id", "source_type", "title", "category"}
    assert "LUSTAT_API" in SOURCE_TYPES and "PUBLICATION_PDF" in SOURCE_TYPES


def test_built_catalog_is_internally_valid() -> None:
    """The committed unified catalog (when present) must validate cleanly."""
    records = load_unified_source_catalog()
    if not records:
        return  # catalog not built in this environment — nothing to validate
    assert catalog_validation_issues(records) == []
    ids = [r["source_id"] for r in records]
    assert len(ids) == len(set(ids))
    for record in records:
        assert record["source_type"] in SOURCE_TYPES


def test_catalog_summary_shape() -> None:
    summary = catalog_summary()
    for key in ("total", "api", "excel", "publications", "commune_level", "categories"):
        assert key in summary


def test_build_unified_catalog_runs() -> None:
    # Builds from saved sub-catalogs; returns an empty list if none exist.
    assert isinstance(build_unified_source_catalog(), list)


def test_report_generation_with_sample_records() -> None:
    sample = [
        _record(source_id="a", category="Housing", source_type="STATEC_EXCEL",
                file_type="xlsx", priority="high", priority_score=6,
                priority_reason="test"),
        _record(source_id="b", category="Population", priority="medium",
                priority_score=3, priority_reason="test"),
    ]
    for rec in sample:
        rec.setdefault("recommended_for_what_changed", False)
    report = generate_report(sample)
    assert "# STATEC Source Catalog Report" in report
    assert "Executive summary" in report
    assert "Housing sources" in report

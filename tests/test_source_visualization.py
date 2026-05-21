from __future__ import annotations

from src.data.source_visualization import (
    VISUALIZATION_STATUSES,
    assess_source_visualization_status,
    build_source_visualization_index,
    get_chart_ready_sources,
    get_sources_needing_mapping,
    get_sources_needing_review,
    load_source_visualization_index,
    visualization_summary,
)


def test_assess_chart_ready_source() -> None:
    row = assess_source_visualization_status(
        {
            "source_id": "api:DF_B1115",
            "source_type": "LUSTAT_API",
            "dataset_id": "DF_B1115",
            "title": "Population",
            "category": "Population",
            "priority": "high",
        }
    )
    assert row["visualization_status"] == "chart_ready"
    assert row["mapped_metric_id"] == "population_growth"


def test_assess_pdf_manual_review() -> None:
    row = assess_source_visualization_status(
        {
            "source_id": "pub:x.pdf",
            "source_type": "PUBLICATION_PDF",
            "title": "PDF publication",
            "category": "Housing",
            "priority": "low",
        }
    )
    assert row["visualization_status"] == "needs_manual_review"


def test_visualization_index_shape_and_counts() -> None:
    index = load_source_visualization_index()
    if not index:
        index = build_source_visualization_index()
    statuses = {row["visualization_status"] for row in index}
    assert statuses.issubset(set(VISUALIZATION_STATUSES))
    summary = visualization_summary(index)
    assert summary["total"] == len(index)
    assert summary["chart_ready"] >= 1
    assert get_chart_ready_sources()
    assert get_sources_needing_mapping()
    assert get_sources_needing_review()

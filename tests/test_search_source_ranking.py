from __future__ import annotations

from src.search import search_source_visualizations


def test_search_ranks_chart_ready_sources_first_for_population() -> None:
    results = search_source_visualizations("population")
    assert results
    statuses = [row["visualization_status"] for row in results[:3]]
    assert "chart_ready" in statuses


def test_search_returns_mapping_states_for_unmapped_terms() -> None:
    results = search_source_visualizations("fertility")
    assert results
    assert any(row["visualization_status"] in {"needs_column_mapping", "chart_ready"} for row in results)


def test_search_returns_tourism_sources_for_related_terms() -> None:
    for query in ["tourism", "tourist arrivals", "hotels", "overnight stays", "accommodation", "D5301"]:
        results = search_source_visualizations(query)
        source_ids = {row["source_id"] for row in results}
        assert {"api:DSD_TOUR_ARR@DF_D5301", "file:D5310.xlsx"} & source_ids


def test_tourism_search_keeps_unmapped_api_out_of_charts() -> None:
    results = search_source_visualizations("D5301")
    d5301 = next(row for row in results if row["source_id"] == "api:DSD_TOUR_ARR@DF_D5301")
    assert d5301["visualization_status"] == "needs_column_mapping"
    assert not d5301.get("mapped_metric_id")

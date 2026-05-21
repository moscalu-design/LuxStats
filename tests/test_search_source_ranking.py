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

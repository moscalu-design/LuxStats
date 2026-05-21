from __future__ import annotations

from src.data.priority_topics import home_question_cards, priority_for_category
from src.data.source_mapping import (
    chart_ready_dataset_ids,
    commune_ready_dataset_ids,
    enrich_with_mapping_status,
    mapping_status,
    source_coverage,
)


def test_priority_topics_rank_public_interest_categories() -> None:
    assert priority_for_category("Housing") > priority_for_category("Tourism")
    assert priority_for_category("Prices / Inflation") > priority_for_category("Public Finance")


def test_home_question_cards_have_destinations_and_status() -> None:
    cards = home_question_cards()
    assert cards
    for card in cards:
        assert card["question"]
        assert card["page"]
        assert card["status"] in {"Chart ready", "Source available, chart mapping pending"}


def test_mapping_status_detects_chart_ready_and_commune_ready() -> None:
    concept_dataset = next(iter(chart_ready_dataset_ids()))
    commune_dataset = next(iter(commune_ready_dataset_ids()))
    assert mapping_status({"dataset_id": concept_dataset, "source_type": "LUSTAT_API"}) == "mapped_to_metric"
    assert mapping_status({"dataset_id": commune_dataset, "source_type": "LUSTAT_API"}) in {
        "mapped_to_metric",
        "mapped_to_commune_portal",
    }


def test_enrich_with_mapping_status_adds_flags() -> None:
    records = enrich_with_mapping_status([
        {"source_id": "x", "dataset_id": "NOPE", "priority": "high", "source_type": "LUSTAT_API"}
    ])
    assert records[0]["mapping_status"] == "unmapped"
    assert records[0]["chart_ready"] is False


def test_source_coverage_shape() -> None:
    coverage = source_coverage("Housing")
    for key in ("total", "chart_ready", "commune_ready", "publications", "unmapped_high_priority"):
        assert key in coverage

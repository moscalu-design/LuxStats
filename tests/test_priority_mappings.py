"""Coverage for the highest-priority manual source mappings.

These tests pin the curated mappings added during the priority-mapping pass:
five new chart-ready concepts and two census commune-portal datasets. They are
deterministic and never touch the network — they only check that the curated
catalog wiring is consistent.
"""

from __future__ import annotations

from src.catalog import catalog_entry, catalog_validation_issues
from src.concepts import concepts_for_topic, get_concept
from src.data.source_mapping import (
    chart_ready_dataset_ids,
    commune_ready_dataset_ids,
    mapping_status,
)
from src.formatting import VALUE_FORMATS, format_value

# concept_id -> (dataset_id, topic, chart)
NEW_CONCEPTS = {
    "permits_by_canton": ("DF_D4113", "Housing", "ranked_bar"),
    "fertility_rate": ("DF_B2207", "Population", "line"),
    "wage_indexation": ("DSD_PRIX_EMS@DF_E5200", "Prices & Inflation", "line"),
    "vacancies_jobseekers": ("DF_B3201", "Labour Market", "line"),
    "gdp_trend": ("DF_E2601", "Economy", "line"),
    "net_migration": ("DF_B2400", "Population", "line"),
    "births_deaths": ("DF_B2110", "Population", "line"),
    "employment_by_sector": ("DSD_EMPLOI_SAL@DF_B3000", "Labour Market", "ranked_bar"),
    "pay_by_education": ("DSD_ESS_EARN_M@DF_C1217", "Salaries", "ranked_bar"),
    "gva_by_sector": ("DF_E2601", "Economy", "ranked_bar"),
}

NEW_COMMUNE_DATASETS = (
    "DSD_CENSUS_GROUP1_3@DF_B1607",
    "DSD_CENSUS_GROUP7_10@DF_B1625",
)


def test_new_concepts_exist_with_expected_wiring() -> None:
    for concept_id, (dataset_id, topic, chart) in NEW_CONCEPTS.items():
        concept = get_concept(concept_id)
        assert concept is not None, f"missing concept {concept_id}"
        assert concept.dataset_id == dataset_id
        assert concept.topic == topic
        assert concept.chart == chart
        assert concept.explanation and concept.unit_note and concept.caveat


def test_new_concepts_are_chart_ready() -> None:
    chart_ready = chart_ready_dataset_ids()
    for dataset_id, _topic, _chart in NEW_CONCEPTS.values():
        assert dataset_id in chart_ready
        assert mapping_status({"dataset_id": dataset_id, "source_type": "LUSTAT_API"}) == "mapped_to_metric"


def test_economy_topic_now_has_a_chart() -> None:
    economy = concepts_for_topic("Economy")
    assert economy, "Economy topic should expose at least one curated chart"
    assert any(c.id == "gdp_trend" for c in economy)


def test_census_commune_datasets_are_mapped_to_commune_portal() -> None:
    commune_ready = commune_ready_dataset_ids()
    for dataset_id in NEW_COMMUNE_DATASETS:
        assert dataset_id in commune_ready
        entry = catalog_entry(dataset_id)
        assert entry is not None
        assert entry["commune_portal"] is True
        assert entry["status"] == "confirmed"
        assert entry["geographic_level"] == "commune"
        # Default filters must reduce each census table to one row per commune.
        assert entry["default_filters"]


def test_catalog_has_no_validation_issues() -> None:
    assert catalog_validation_issues() == []


def test_rate_value_format_is_registered() -> None:
    assert "rate" in VALUE_FORMATS
    assert format_value(2.236, "rate") == "2.24"

from __future__ import annotations

from src.concepts import CONCEPTS, all_concepts, concepts_for_topic, get_concept

_VALID_CHARTS = {"line", "ranked_bar", "bar"}
_VALID_LEVELS = {"national", "commune", "region", "unknown"}
_VALID_DIFFICULTY = {"beginner", "intermediate"}


def test_concept_ids_are_unique() -> None:
    ids = [c.id for c in CONCEPTS]
    assert len(ids) == len(set(ids))


def test_concepts_have_required_metadata() -> None:
    for concept in all_concepts():
        assert concept.title and concept.description
        assert concept.dataset_id
        assert concept.keywords, f"{concept.id} has no search keywords"
        assert concept.chart in _VALID_CHARTS
        assert concept.geographic_level in _VALID_LEVELS
        assert concept.difficulty in _VALID_DIFFICULTY


def test_concept_chart_label_is_friendly() -> None:
    for concept in all_concepts():
        assert concept.chart_label
        assert "_" not in concept.chart_label


def test_get_concept_round_trips() -> None:
    for concept in all_concepts():
        assert get_concept(concept.id) is concept
    assert get_concept("does_not_exist") is None


def test_concepts_for_topic_filters() -> None:
    salary = concepts_for_topic("Salaries")
    assert salary
    assert all(c.topic == "Salaries" for c in salary)

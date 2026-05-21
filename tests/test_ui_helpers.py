from __future__ import annotations

from src.concepts import all_concepts
from src.data.geography import commune_boundaries_available, geography_status
from src.ui.explanations import get_explanation


def test_geography_status_is_honest_when_no_boundaries() -> None:
    status = geography_status()
    assert status["boundaries_available"] == commune_boundaries_available()
    if not status["boundaries_available"]:
        assert "not available yet" in status["message"]


def test_every_concept_has_a_four_part_explanation() -> None:
    for concept in all_concepts():
        parts = get_explanation(concept)
        assert set(parts) == {"what", "how", "watch", "source"}
        assert all(parts.values()), f"{concept.id} has an empty explanation part"

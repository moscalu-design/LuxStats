from __future__ import annotations

from pathlib import Path

from src.data.analysis_cards import (
    all_cards,
    card_validation_issues,
    commune_cards,
    comparison_cards,
    popular_cards,
)

ROOT = Path(__file__).resolve().parents[1]


def test_cards_validate_cleanly() -> None:
    assert card_validation_issues() == []


def test_card_sections_are_populated() -> None:
    assert popular_cards()
    assert comparison_cards()
    assert commune_cards()


def test_card_pages_point_at_real_files() -> None:
    for card in all_cards():
        if card.page:
            assert (ROOT / card.page).exists(), f"{card.id} -> missing {card.page}"


def test_card_difficulty_values_are_known() -> None:
    for card in all_cards():
        assert card.difficulty in {"beginner", "intermediate"}

from __future__ import annotations

from src.ui.navigation import (
    NAV_GROUPS,
    all_nav_items,
    nav_page_paths,
    primary_items,
    topic_items,
)


def test_navigation_groups_are_product_ordered() -> None:
    """Primary journeys first, topics next, advanced tools last."""
    assert [group for group, _items in NAV_GROUPS] == [
        "Primary",
        "Topics",
        "More tools",
    ]


def test_primary_group_leads_with_search() -> None:
    """Home and search must be the obvious starting points."""
    labels = [item.label for item in primary_items()]
    assert labels == ["Home", "Find a statistic", "Compare", "What changed?"]


def test_topics_are_compact_and_complete() -> None:
    labels = [item.label for item in topic_items()]
    assert labels == [
        "Housing",
        "Salaries & income",
        "Population",
        "Labour market",
        "Prices & inflation",
        "Economy",
        "Tourism",
        "AI adoption",
    ]


def test_advanced_tools_live_in_more_tools_group() -> None:
    """Advanced/source pages must not sit in the primary journey."""
    more = {item.page for item in all_nav_items() if item.group == "More tools"}
    assert "pages/13_Source_Library.py" in more
    assert "pages/11_Dataset_Explorer.py" in more
    assert "pages/3_Commune_Portal.py" in more
    # The Commune Portal is reachable, but not a top-level primary item.
    primary_pages = {item.page for item in primary_items()}
    assert "pages/3_Commune_Portal.py" not in primary_pages


def test_navigation_has_no_duplicate_pages() -> None:
    items = all_nav_items()
    pages = [item.page for item in items]
    assert len(pages) == len(set(pages))
    assert "app.py" in nav_page_paths()
    assert "pages/13_Source_Library.py" in nav_page_paths()
    assert "pages/15_Tourism.py" in nav_page_paths()


def test_every_product_page_is_reachable() -> None:
    """All 16 product pages plus Home are in the single custom sidebar."""
    paths = nav_page_paths()
    assert len(paths) == 17  # app.py + 16 pages
    for n in range(1, 17):
        assert any(f"/{n}_" in p for p in paths)

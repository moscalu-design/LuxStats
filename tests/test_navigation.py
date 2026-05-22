from __future__ import annotations

from src.ui.navigation import NAV_GROUPS, all_nav_items, nav_page_paths


def test_navigation_groups_are_product_ordered() -> None:
    assert [group for group, _items in NAV_GROUPS] == [
        "Main",
        "Topics",
        "Data & Sources",
        "About / Help",
    ]


def test_navigation_labels_match_public_structure() -> None:
    labels = [item.label for item in all_nav_items()]
    assert labels == [
        "Home",
        "Find a Statistic",
        "Compare",
        "Build a Chart",
        "What Changed?",
        "Housing",
        "Salaries & Income",
        "Population",
        "Labour Market",
        "Prices & Inflation",
        "Economy",
        "Tourism",
        "Dataset Explorer",
        "Source Library",
        "About Data",
    ]
    assert "Commune Portal" not in labels


def test_navigation_has_no_duplicate_pages() -> None:
    items = all_nav_items()
    pages = [item.page for item in items]
    assert len(pages) == len(set(pages))
    assert "app.py" in nav_page_paths()
    assert "pages/13_Source_Library.py" in nav_page_paths()
    assert "pages/15_Tourism.py" in nav_page_paths()

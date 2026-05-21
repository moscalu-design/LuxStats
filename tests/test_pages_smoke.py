from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_TEXT = {path.name: path.read_text(encoding="utf-8") for path in (ROOT / "pages").glob("*.py")}


def test_expected_pages_are_present() -> None:
    expected = {
        "1_Home.py",
        "2_Housing.py",
        "3_Salaries.py",
        "4_Population.py",
        "5_Labour_Market.py",
        "6_Prices_Inflation.py",
        "7_Dataset_Explorer.py",
        "8_About_Data.py",
        "9_Commune_Portal.py",
    }
    assert expected.issubset(PAGE_TEXT)


def test_topic_pages_render_topic_page() -> None:
    for page in ["2_Housing.py", "4_Population.py", "5_Labour_Market.py", "6_Prices_Inflation.py"]:
        assert "render_topic_page(" in PAGE_TEXT[page]


def test_dataset_explorer_has_friendly_failure_states() -> None:
    source = PAGE_TEXT["7_Dataset_Explorer.py"]
    assert "Could not load dataflows" in source
    assert "Fetch failed" in source
    assert "No curated entries match" in source


def test_commune_portal_has_required_tabs_and_downloads() -> None:
    source = PAGE_TEXT["9_Commune_Portal.py"]
    for label in ["Overview", "Population", "Housing", "Salaries", "Labour", "All data", "Sources"]:
        assert label in source
    assert "Download all available commune data" in source

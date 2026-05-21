from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_TEXT = {path.name: path.read_text(encoding="utf-8") for path in (ROOT / "pages").glob("*.py")}


def test_expected_pages_are_present() -> None:
    expected = {
        "1_Find_a_Statistic.py",
        "2_Build_a_Chart.py",
        "3_Commune_Portal.py",
        "4_Compare.py",
        "5_What_Changed.py",
        "6_Housing.py",
        "7_Salaries.py",
        "8_Population.py",
        "9_Labour_Market.py",
        "10_Prices_Inflation.py",
        "11_Dataset_Explorer.py",
        "12_About_Data.py",
        "13_Source_Library.py",
    }
    assert expected.issubset(PAGE_TEXT)


def test_topic_pages_render_topic_page() -> None:
    for page in ["6_Housing.py", "8_Population.py", "9_Labour_Market.py", "10_Prices_Inflation.py"]:
        assert "render_topic_page(" in PAGE_TEXT[page]


def test_dataset_explorer_has_friendly_failure_states() -> None:
    source = PAGE_TEXT["11_Dataset_Explorer.py"]
    assert "Could not load dataflows" in source
    assert "Fetch failed" in source
    assert "No curated entries match" in source


def test_commune_portal_has_required_tabs_and_downloads() -> None:
    source = PAGE_TEXT["3_Commune_Portal.py"]
    for label in ["Overview", "Population", "Housing", "Salaries", "Labour", "Map", "All data", "Sources"]:
        assert label in source
    assert "Download all available commune data" in source


def test_product_pages_use_curated_components() -> None:
    assert "render_chart_builder(" in PAGE_TEXT["2_Build_a_Chart.py"]
    assert "render_comparison_chart(" in PAGE_TEXT["4_Compare.py"]
    assert "calculate_latest_change(" in PAGE_TEXT["5_What_Changed.py"]


def test_no_llm_or_chatbot_feature_on_pages() -> None:
    """The portal must stay deterministic — no chatbot / GPT feature in pages."""
    banned = ["chatbot", "chat_input", "openai", "gpt-", "ask the ai"]
    for name, source in PAGE_TEXT.items():
        lowered = source.lower()
        for token in banned:
            assert token not in lowered, f"{name} contains banned token {token!r}"

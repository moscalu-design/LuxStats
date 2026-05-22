from __future__ import annotations

from src.ui.page_header import PAGE_HEADERS, get_page_header


def test_required_page_headers_exist() -> None:
    for page_id in [
        "home", "find", "commune", "compare", "builder", "changes",
        "housing", "salaries", "population", "labour", "prices", "economy",
        "tourism", "source_library", "dataset_explorer", "about",
    ]:
        header = get_page_header(page_id)
        assert header.title
        assert header.subtitle


def test_headers_are_not_generic_duplicates() -> None:
    titles = [header.title for header in PAGE_HEADERS.values()]
    assert len(titles) == len(set(titles))
    assert get_page_header("source_library").title == "Source Library"
    assert get_page_header("about").title == "About Data"

from __future__ import annotations

from src.data.categorization import (
    CATEGORIES,
    categorize,
    extract_keywords,
    infer_geographic_level,
    looks_like_housing_data,
    looks_like_short_term_indicator,
)


def test_housing_keywords_map_to_housing() -> None:
    assert categorize("Acquisition prices for dwellings") == "Housing"
    assert categorize("Prix des logements par commune") == "Housing"
    assert categorize("rental market and rents") == "Housing"


def test_salary_keywords_map_to_salaries() -> None:
    assert categorize("Average salary by sector") == "Salaries / Income"
    assert categorize("Salaires et rémunération") == "Salaries / Income"


def test_commune_and_geography_keywords() -> None:
    assert categorize("Statistics by geographical breakdown — canton") in {
        "Communes / Geography", "Population",
    }
    assert infer_geographic_level("Population by municipality") == "commune"
    assert infer_geographic_level("Canton-level employment") == "canton"
    assert infer_geographic_level("National GDP for the country") == "national"
    assert infer_geographic_level("a vague title") == "unknown"


def test_inflation_and_labour_keywords() -> None:
    assert categorize("Consumer price index (CPI)") == "Prices / Inflation"
    assert categorize("Unemployment and employment by month") == "Labour Market"


def test_unknown_text_falls_back_to_other() -> None:
    assert categorize("") == "Other / Unknown"
    assert categorize("xyzzy 12345") == "Other / Unknown"


def test_categories_list_is_complete_and_has_fallback() -> None:
    assert "Other / Unknown" in CATEGORIES
    assert len(CATEGORIES) == len(set(CATEGORIES))


def test_keyword_extraction_skips_stopwords() -> None:
    kws = extract_keywords("The price of housing in the communes of Luxembourg")
    assert "the" not in kws
    assert "housing" in kws


def test_helper_flags() -> None:
    assert looks_like_housing_data("Le logement en chiffres")
    assert looks_like_short_term_indicator("Short-term indicator: monthly")
    assert not looks_like_short_term_indicator("Annual census table")

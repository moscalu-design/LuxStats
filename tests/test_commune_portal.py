from __future__ import annotations

import pandas as pd

from src.data.commune_portal import (
    CommuneDataset,
    calculate_commune_trend,
    compare_commune_to_national_average,
    filter_dataset_for_commune,
    get_latest_commune_value,
    rank_commune_against_others,
)
from src.data.communes import commune_suggestions, extract_commune_from_query, list_communes, normalize_commune_name
from src.search import search_communes


def test_commune_list_contains_current_luxembourg_communes() -> None:
    communes = list_communes()
    assert len(communes) == 100
    assert {"Hesperange", "Luxembourg", "Esch-sur-Alzette", "Dudelange"}.issubset(communes)


def test_commune_aliases_normalize_common_inputs() -> None:
    assert normalize_commune_name("Luxembourg City") == "Luxembourg"
    assert normalize_commune_name("Ville de Luxembourg") == "Luxembourg"
    assert normalize_commune_name("Luxembourg-Ville") == "Luxembourg"
    assert normalize_commune_name("Esch sur Alzette") == "Esch-sur-Alzette"
    assert normalize_commune_name("Hesperange") == "Hesperange"


def test_commune_suggestions_are_cautious() -> None:
    assert commune_suggestions("hesp") == ["Hesperange"]
    assert commune_suggestions("not-a-real-place") == []


def test_extract_commune_from_query() -> None:
    assert extract_commune_from_query("population Hesperange") == "Hesperange"
    assert extract_commune_from_query("housing Luxembourg City") == "Luxembourg"


def test_commune_search_result_mentions_salary_caveat() -> None:
    result = search_communes("commune salaries Hesperange")
    assert result[0]["commune"] == "Hesperange"
    assert result[0]["tab"] == "Salaries"


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "TIME_PERIOD": ["2022", "2023", "2023", "2022", "2023"],
            "COMMUNE_LABEL": ["Hesperange", "Hesperange", "Luxembourg", "Dudelange", "Dudelange"],
            "OBS_VALUE": [100, 120, 300, 80, 90],
        }
    )


def test_filter_dataset_for_commune_by_label() -> None:
    dataset = CommuneDataset("demo", "Demo", "Population", "", "COMMUNE_LABEL", "OBS_VALUE", "TIME_PERIOD", "cached")
    result = filter_dataset_for_commune(_sample_df(), "Hesperange", dataset)
    assert result["OBS_VALUE"].tolist() == [100, 120]


def test_latest_trend_average_and_rank_helpers() -> None:
    df = _sample_df()
    commune_rows = filter_dataset_for_commune(df, "Hesperange")
    assert get_latest_commune_value(commune_rows) == {"value": 120.0, "period": "2023"}
    trend = calculate_commune_trend(commune_rows)
    assert trend is not None
    assert trend["delta"] == 20.0
    comparison = compare_commune_to_national_average(df, "Hesperange")
    assert comparison is not None
    assert comparison["commune_value"] == 120.0
    rank = rank_commune_against_others(df, "Hesperange")
    assert rank is not None
    assert rank["rank"] == 2

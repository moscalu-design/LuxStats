from __future__ import annotations

import pandas as pd

from src.transforms import index_rebase, ranking_by_latest, time_series, year_over_year_growth


def test_time_series_averages_values_by_period() -> None:
    df = pd.DataFrame({"TIME_PERIOD": ["2022", "2022", "2023"], "OBS_VALUE": [10, 20, 40]})
    result = time_series(df)
    assert result.to_dict("records") == [
        {"TIME_PERIOD": "2022", "OBS_VALUE": 15.0},
        {"TIME_PERIOD": "2023", "OBS_VALUE": 40.0},
    ]


def test_ranking_by_latest_uses_latest_period() -> None:
    df = pd.DataFrame(
        {
            "TIME_PERIOD": ["2022", "2023", "2023"],
            "COMMUNE": ["A", "A", "B"],
            "OBS_VALUE": [5, 10, 20],
        }
    )
    result = ranking_by_latest(df, "COMMUNE")
    assert result["COMMUNE"].tolist() == ["B", "A"]


def test_index_rebase_sets_base_to_100() -> None:
    df = pd.DataFrame({"TIME_PERIOD": ["2020", "2021"], "OBS_VALUE": [50, 75]})
    result = index_rebase(df, base_period="2020")
    assert result["INDEX_VALUE"].round(1).tolist() == [100.0, 150.0]


def test_year_over_year_growth_percent() -> None:
    df = pd.DataFrame({"TIME_PERIOD": ["2020", "2021"], "OBS_VALUE": [100, 125]})
    result = year_over_year_growth(df)
    assert pd.isna(result.loc[0, "YOY_GROWTH"])
    assert result.loc[1, "YOY_GROWTH"] == 25.0

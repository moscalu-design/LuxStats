from __future__ import annotations

import pandas as pd

from src.data.time_utils import (
    calculate_period_change,
    detect_frequency,
    filter_by_period_range,
    get_latest_period,
    get_previous_period,
    get_period_range_options,
    parse_period_value,
)


def test_parse_period_value_handles_common_statec_shapes() -> None:
    assert parse_period_value("2024").label == "2024"
    assert parse_period_value("2024-Q1").label == "2024 Q1"
    assert parse_period_value("2024Q2").label == "2024 Q2"
    assert parse_period_value("2024-T3").label == "2024 Q3"
    assert parse_period_value("2024-M01").label == "2024-01"
    assert parse_period_value("2024-02").label == "2024-02"
    assert parse_period_value("Jan 2024").label == "2024-01"


def test_detect_frequency_prefers_mode() -> None:
    assert detect_frequency(pd.Series(["2020", "2021", "2022"])) == "annual"
    assert detect_frequency(pd.Series(["2024-Q1", "2024-Q2"])) == "quarterly"
    assert detect_frequency(pd.Series(["2024-01", "2024-02"])) == "monthly"


def test_period_range_filter_and_latest_previous() -> None:
    df = pd.DataFrame({"TIME_PERIOD": ["2020", "2021", "2022"], "OBS_VALUE": [1, 2, 3]})
    assert get_latest_period(df, "TIME_PERIOD") == "2022"
    assert get_previous_period(df, "TIME_PERIOD") == "2021"
    options = get_period_range_options(df, "TIME_PERIOD")
    filtered = filter_by_period_range(df, "TIME_PERIOD", *options["Last 5 years"])
    assert filtered["OBS_VALUE"].tolist() == [1, 2, 3]


def test_calculate_period_change() -> None:
    df = pd.DataFrame(
        {
            "TIME_PERIOD": ["2023", "2024", "2023", "2024"],
            "COMMUNE": ["A", "A", "B", "B"],
            "OBS_VALUE": [100, 120, 50, 40],
        }
    )
    result = calculate_period_change(df, "COMMUNE", "OBS_VALUE", "TIME_PERIOD")
    assert result.loc[result["COMMUNE"] == "A", "change"].iloc[0] == 20
    assert result.loc[result["COMMUNE"] == "B", "pct_change"].iloc[0] == -20

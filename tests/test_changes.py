from __future__ import annotations

import pandas as pd

from src.analysis.changes import (
    calculate_latest_change,
    calculate_top_decreases,
    calculate_top_increases,
    get_recently_updated_metrics,
)


def _commune_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "TIME_PERIOD": ["2022", "2023", "2022", "2023", "2022", "2023"],
            "GEO_LABEL": [
                "Hesperange", "Hesperange",
                "Luxembourg", "Luxembourg",
                "Dudelange", "Dudelange",
            ],
            "OBS_VALUE": [100, 130, 200, 210, 80, 60],
        }
    )


def test_recently_updated_metrics_has_expected_shape() -> None:
    rows = get_recently_updated_metrics()
    assert rows
    for row in rows:
        assert {"metric_id", "title", "topic", "dataset_id", "cached"}.issubset(row)


def test_latest_change_unknown_metric_returns_none() -> None:
    assert calculate_latest_change("not_a_metric") is None


def test_top_increases_and_decreases() -> None:
    increases = calculate_top_increases(_commune_df(), "GEO_LABEL")
    assert not increases.empty
    # Hesperange grew 30%, the strongest increase.
    assert increases.iloc[0]["GEO_LABEL"] == "Hesperange"

    decreases = calculate_top_decreases(_commune_df(), "GEO_LABEL")
    assert not decreases.empty
    # Dudelange fell 25%, the strongest decrease.
    assert decreases.iloc[0]["GEO_LABEL"] == "Dudelange"


def test_changes_handle_empty_or_single_period() -> None:
    assert calculate_top_increases(pd.DataFrame(), "GEO_LABEL").empty
    single = pd.DataFrame(
        {"TIME_PERIOD": ["2023"], "GEO_LABEL": ["Luxembourg"], "OBS_VALUE": [10]}
    )
    assert calculate_top_increases(single, "GEO_LABEL").empty

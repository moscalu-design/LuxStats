from __future__ import annotations

import pandas as pd

from src.analysis.comparison import (
    build_commune_comparison_dataframe,
    build_comparison_dataframe,
    get_commune_comparison_metrics,
    get_comparable_metrics,
    render_comparison_chart,
)


def test_comparable_metrics_have_a_series_dimension() -> None:
    metrics = get_comparable_metrics()
    assert metrics
    assert all(c.series_dim for c in metrics)


def test_commune_comparison_metrics_are_confirmed() -> None:
    datasets = get_commune_comparison_metrics()
    assert datasets
    assert all(not d.dataset_id.startswith("TODO_CONFIRM_") for d in datasets)


def test_build_comparison_handles_unknown_metric() -> None:
    df = build_comparison_dataframe("not_a_metric", ["A"])
    assert df.empty
    assert list(df.columns) == ["Year", "Series", "Value"]


def test_build_comparison_handles_empty_selection() -> None:
    df = build_comparison_dataframe("salary_by_sector", [])
    assert df.empty


def test_build_commune_comparison_handles_empty_communes() -> None:
    df = build_commune_comparison_dataframe("DF_X021", [])
    assert df.empty
    assert list(df.columns) == ["Year", "Series", "Value"]


def test_render_comparison_chart_handles_empty_frame() -> None:
    assert render_comparison_chart(pd.DataFrame()) is None
    assert render_comparison_chart(None) is None


def test_render_comparison_chart_draws_for_real_frame() -> None:
    df = pd.DataFrame(
        {
            "Year": [2020, 2021, 2020, 2021],
            "Series": ["A", "A", "B", "B"],
            "Value": [1.0, 2.0, 3.0, 4.0],
        }
    )
    fig = render_comparison_chart(df, value_format="euro", chart="line")
    assert fig is not None
    bar = render_comparison_chart(df, value_format="number", chart="bar")
    assert bar is not None

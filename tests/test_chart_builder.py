from __future__ import annotations

from src.ui.chart_builder import (
    build_chart_from_selection,
    get_metrics_for_topic,
    get_topics,
)


def test_get_topics_returns_topics_with_metrics() -> None:
    topics = get_topics()
    assert topics
    for topic in topics:
        assert get_metrics_for_topic(topic)


def test_build_chart_handles_unknown_metric() -> None:
    df = build_chart_from_selection({"metric_id": "not_a_metric"})
    assert df.empty
    assert list(df.columns) == ["Year", "Series", "Value"]


def test_build_chart_handles_missing_metric_id() -> None:
    df = build_chart_from_selection({})
    assert df.empty

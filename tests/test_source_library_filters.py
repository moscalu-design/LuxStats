from __future__ import annotations

from src.data.source_visualization import load_source_visualization_index
from src.ui.source_visualizer import readiness_dataframe, readiness_options, status_label


def test_readiness_filter_options_include_safe_states() -> None:
    options = readiness_options()
    assert "All" in options
    assert "chart_ready" in options
    assert "needs_column_mapping" in options
    assert "needs_manual_review" in options


def test_readiness_dataframe_has_user_facing_columns() -> None:
    rows = load_source_visualization_index()[:3]
    df = readiness_dataframe(rows)
    for column in ["Title", "Category", "Type", "Readiness", "Action", "Reason"]:
        assert column in df.columns


def test_status_label_is_human_readable() -> None:
    assert status_label("needs_column_mapping") == "Needs mapping"

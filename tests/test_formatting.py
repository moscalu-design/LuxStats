"""Tests for human-friendly value and delta formatting."""

from __future__ import annotations

from src.formatting import format_delta, format_value


def test_format_value_handles_formats_and_missing() -> None:
    assert format_value(1234, "number") == "1,234"
    assert format_value(1234.5, "euro") == "€1,234"
    assert format_value(2.5, "percent") == "2.5%"
    assert format_value(2.236, "rate") == "2.24"
    assert format_value(None) == "—"


def test_format_delta_negative_starts_with_ascii_minus() -> None:
    """st.metric reads the arrow/colour from a leading ASCII '-'.

    A typographic minus ('−', U+2212) would make a negative change show a
    green upward arrow, so negative deltas must start with '-' (U+002D).
    """
    negative = format_delta(-1500, "euro")
    assert negative is not None
    assert negative.startswith("-")
    assert "−" not in negative
    assert negative == "-€1,500"


def test_format_delta_positive_keeps_plus_sign() -> None:
    positive = format_delta(3.2, "percent")
    assert positive == "+3.2%"
    assert not positive.startswith("-")


def test_format_delta_missing_is_none() -> None:
    assert format_delta(None) is None

"""Plain-language explanation layer for charts.

No language model is used. Explanations are built from static templates plus
the curated metadata already stored on each :class:`~src.concepts.Concept`.
Every explanation answers four short questions: what this shows, how to read
it, what to watch out for, and where the data comes from.
"""

from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from src.concepts import Concept

# How to read each chart type, in plain language.
_HOW_TO_READ: dict[str, str] = {
    "line": "Follow each line from left to right — that is change over time. "
    "A rising line means the value is going up.",
    "ranked_bar": "Each bar is one category. Longer bars are higher values. "
    "The chart is sorted so the biggest values are easy to spot.",
    "bar": "Compare the height of the bars — taller means a higher value.",
}

_GENERIC_CAVEAT = (
    "Figures are official but definitions can be technical. The most recent "
    "period may still be provisional and can be revised later."
)


def get_explanation(concept: Concept) -> dict[str, str]:
    """Return the four-part plain-language explanation for a concept."""
    what = concept.explanation or concept.description
    how = _HOW_TO_READ.get(concept.chart, _HOW_TO_READ["line"])
    if concept.unit_note:
        how = f"{how} {concept.unit_note}"
    watch = concept.caveat or _GENERIC_CAVEAT
    source = "Official data from STATEC / LUSTAT, Luxembourg's statistics office."
    return {"what": what, "how": how, "watch": watch, "source": source}


def render_chart_explanation(concept: Concept) -> None:
    """Render the short 'what this means' block shown under a chart."""
    parts = get_explanation(concept)
    st.markdown(
        f"<div class='lux-explain'>"
        f"<strong>What this shows.</strong> {escape(parts['what'])}<br>"
        f"<strong>How to read it.</strong> {escape(parts['how'])}<br>"
        f"<strong>Watch out for.</strong> {escape(parts['watch'])}"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_source_caveats(metadata: dict[str, Any]) -> None:
    """Render a caveat note from dataset metadata, when one is available."""
    note = metadata.get("notes") or metadata.get("caveat")
    if not note:
        note = _GENERIC_CAVEAT
    st.markdown(
        f"<div class='lux-caveat'><strong>Good to know.</strong> {escape(str(note))}</div>",
        unsafe_allow_html=True,
    )

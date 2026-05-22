"""Friendly result cards.

These replace raw technical dataset rows with human-readable cards. A metric
card describes one curated statistic; an analysis card describes a ready-made
journey; a question card is a plain-language entry point. Dataset IDs and SDMX
terms stay inside an advanced expander.
"""

from __future__ import annotations

import streamlit as st

from src.concepts import Concept
from src.data.analysis_cards import AnalysisCard

# Plain-language labels for a concept's geographic level.
_LEVEL_TEXT = {
    "national": "National",
    "commune": "Commune-level",
    "region": "Regional",
    "unknown": "Geography varies",
}


def open_concept(concept_id: str) -> None:
    """Mark a concept to be rendered inline by the hosting page."""
    st.session_state["open_concept"] = concept_id


def render_metric_card(concept: Concept, *, key_prefix: str, on_open=None) -> None:
    """Render one friendly metric result card."""
    with st.container(border=True):
        st.markdown(
            f"<span class='lux-tag'>{concept.topic}</span>"
            f"<span class='lux-tag lux-status-chart-ready'>Ready to chart</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**{concept.title}**")
        st.caption(concept.description)
        meta_bits = [
            _LEVEL_TEXT.get(concept.geographic_level, concept.geographic_level),
            concept.chart_label,
        ]
        st.markdown(
            f"<div class='lux-card-meta'>{' · '.join(meta_bits)} · STATEC / LUSTAT</div>",
            unsafe_allow_html=True,
        )
        st.button(
            "Open chart",
            key=f"{key_prefix}_{concept.id}",
            use_container_width=True,
            type="primary",
            on_click=on_open or open_concept,
            args=(concept.id,),
        )
        with st.expander("Advanced details"):
            st.caption(f"Dataset ID: `{concept.dataset_id}`")
            st.caption(f"Topic: {concept.topic} · Difficulty: {concept.difficulty}")
            if concept.unit_note:
                st.caption(f"Measures: {concept.unit_note}")


def render_metric_grid(concepts: list[Concept], *, key_prefix: str, columns: int = 2,
                       on_open=None) -> None:
    """Lay metric cards out in a responsive grid."""
    for start in range(0, len(concepts), columns):
        cols = st.columns(columns)
        for col, concept in zip(cols, concepts[start:start + columns]):
            with col:
                render_metric_card(concept, key_prefix=key_prefix, on_open=on_open)


def render_analysis_card(card: AnalysisCard, *, key_prefix: str) -> None:
    """Render one guided analysis journey card."""
    with st.container(border=True):
        st.markdown(f"<span class='lux-tag'>{card.topic}</span>", unsafe_allow_html=True)
        st.markdown(f"**{card.title}**")
        st.caption(card.blurb)
        if st.button("Open", key=f"{key_prefix}_{card.id}", use_container_width=True):
            if card.concept_id:
                open_concept(card.concept_id)
                st.rerun()
            elif card.page:
                st.switch_page(card.page)


def render_question_card(card: dict[str, object], *, key_prefix: str) -> None:
    """Render a compact, plain-language entry-point card."""
    with st.container(border=True):
        chart_ready = bool(card.get("chart_ready"))
        status_class = "lux-status-chart-ready" if chart_ready else "lux-status-unresolved"
        status_text = "Chart ready" if chart_ready else "Source available"
        st.markdown(
            f"<span class='lux-tag'>{card['topic']}</span>"
            f"<span class='lux-tag {status_class}'>{status_text}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**{card['question']}**")
        st.caption(str(card["description"]))
        if st.button("Open", key=f"{key_prefix}_{card['id']}", use_container_width=True):
            if card.get("concept_id"):
                open_concept(str(card["concept_id"]))
                st.rerun()
            else:
                st.switch_page(str(card["page"]))


def render_question_grid(cards: list[dict[str, object]], *, key_prefix: str,
                         columns: int = 4) -> None:
    """Lay plain-language question cards out in a compact grid."""
    for start in range(0, len(cards), columns):
        cols = st.columns(columns)
        for col, card in zip(cols, cards[start:start + columns]):
            with col:
                render_question_card(card, key_prefix=key_prefix)


def render_analysis_grid(cards: list[AnalysisCard], *, key_prefix: str,
                         columns: int = 3) -> None:
    """Lay analysis cards out in a responsive grid."""
    for start in range(0, len(cards), columns):
        cols = st.columns(columns)
        for col, card in zip(cols, cards[start:start + columns]):
            with col:
                render_analysis_card(card, key_prefix=key_prefix)

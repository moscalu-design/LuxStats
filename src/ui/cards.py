"""Friendly metric and analysis cards.

These replace raw technical dataset rows with human-readable cards. A metric
card describes one curated statistic; an analysis card describes a ready-made
journey. Both keep dataset IDs and SDMX terms inside an advanced expander.
"""

from __future__ import annotations

import streamlit as st

from src.concepts import Concept
from src.data.analysis_cards import AnalysisCard

# Plain-language labels for a concept's geographic level.
_LEVEL_TEXT = {
    "national": "🇱🇺 National",
    "commune": "📍 Commune-level",
    "region": "🗺️ Regional",
    "unknown": "Geography varies",
}


def open_concept(concept_id: str) -> None:
    """Mark a concept to be rendered inline by the hosting page."""
    st.session_state["open_concept"] = concept_id


def render_metric_card(concept: Concept, *, key_prefix: str, on_open=None) -> None:
    """Render one friendly metric result card.

    ``on_open`` is an optional callback invoked with the concept id; when it is
    omitted the card stores the concept in session state via :func:`open_concept`.
    """
    with st.container(border=True):
        st.markdown(
            f"<span class='lux-tag'>{concept.topic}</span>", unsafe_allow_html=True
        )
        st.markdown(f"**{concept.title}**")
        st.caption(concept.description)
        meta_bits = [
            _LEVEL_TEXT.get(concept.geographic_level, concept.geographic_level),
            f"Best shown as: {concept.chart_label}",
            "STATEC / LUSTAT",
        ]
        st.caption(" · ".join(meta_bits))
        st.button(
            "Open chart →",
            key=f"{key_prefix}_{concept.id}",
            use_container_width=True,
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
        st.markdown(
            f"<span class='lux-tag'>{card.topic}</span> "
            f"<span class='lux-muted'>{card.difficulty.capitalize()}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"### {card.icon} {card.title}")
        st.caption(card.blurb)
        if st.button("Open →", key=f"{key_prefix}_{card.id}", use_container_width=True):
            if card.concept_id:
                open_concept(card.concept_id)
                st.rerun()
            elif card.page:
                st.switch_page(card.page)


def render_analysis_grid(cards: list[AnalysisCard], *, key_prefix: str,
                         columns: int = 3) -> None:
    """Lay analysis cards out in a responsive grid."""
    for start in range(0, len(cards), columns):
        cols = st.columns(columns)
        for col, card in zip(cols, cards[start:start + columns]):
            with col:
                render_analysis_card(card, key_prefix=key_prefix)

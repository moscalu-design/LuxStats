from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.commune_portal import get_commune_profile
from src.data.communes import commune_suggestions, list_communes, normalize_commune_name
from src.ui.commune_components import render_all_data_table, render_section_items
from src.ui.maps import render_commune_map, render_map_empty_state
from src.ui_components import configure_page, download_csv, page_hero, render_sidebar, section_header

configure_page("LuxStats - Commune Portal")
render_sidebar()


def _initial_commune() -> str:
    query_commune = st.query_params.get("commune")
    if query_commune:
        normalized = normalize_commune_name(str(query_commune))
        if normalized:
            return normalized
    stored = st.session_state.get("selected_commune")
    if stored and normalize_commune_name(stored):
        return normalize_commune_name(stored) or "Hesperange"
    return "Hesperange"


page_hero(
    "Commune Portal",
    "Choose a commune and explore local statistics in one place.",
    "A local profile dashboard for official commune-level STATEC / LUSTAT data. "
    "If a topic is only available nationally, it stays out of the commune view.",
)

all_communes = list_communes()
default_commune = _initial_commune()
selected = st.selectbox(
    "Choose a commune",
    all_communes,
    index=all_communes.index(default_commune) if default_commune in all_communes else 0,
    placeholder="Search Hesperange, Luxembourg City, Esch-sur-Alzette...",
)
st.session_state["selected_commune"] = selected
st.query_params["commune"] = selected

with st.expander("Not sure of the spelling?", expanded=False):
    typed = st.text_input("Find a commune", placeholder="Luxembourg City, Luxembourg-Ville, Hesperange...")
    if typed:
        suggestions = commune_suggestions(typed)
        if suggestions:
            st.write("Did you mean:")
            cols = st.columns(min(3, len(suggestions)))
            for col, suggestion in zip(cols, suggestions):
                if col.button(suggestion, use_container_width=True):
                    st.session_state["selected_commune"] = suggestion
                    st.query_params["commune"] = suggestion
                    st.rerun()
        else:
            st.info("No clear commune match found. Try a nearby spelling from the selector above.")

with st.spinner("Loading official commune-level datasets..."):
    profile = get_commune_profile(selected)

st.markdown(f"## {profile['commune']}")
st.caption(f"Local statistics profile · Canton: {profile.get('canton') or 'Not available'}")

metrics = profile["overview_metrics"][:4]
cols = st.columns(4)
for col, metric in zip(cols, metrics):
    with col:
        value = metric["value"]
        display = f"{int(value):,}" if metric["label"] == "Available local datasets" else f"{value:,.0f}"
        trend = metric.get("trend") or {}
        delta = None
        if trend.get("pct_change") is not None:
            delta = f"{trend['pct_change']:.1f}%"
        st.metric(metric["label"], display, delta=delta, help=metric.get("dataset"))

if profile["ready_count"] == 0:
    st.info(
        "No cached commune-level dataset currently contains rows for this commune. "
        "The portal is ready for official local datasets once their exact STATEC / LUSTAT mappings are confirmed or fetched in the Dataset Explorer."
    )

tabs = st.tabs(["Overview", "Population", "Housing", "Salaries", "Labour", "Map", "All data", "Sources"])

with tabs[0]:
    section_header("Overview", "The best available local indicators for this commune.")
    ready_items = [item for item in profile["loaded_datasets"] if item.get("status") == "ready"]
    if ready_items:
        render_section_items("Best available trends", ready_items[:2], "overview")
    else:
        st.info(
            "There is not enough connected commune-level data yet to build a full profile. "
            "Confirmed population, housing, and labour dataflows can be added to the catalog without changing this page."
        )

with tabs[1]:
    render_section_items("Population", profile["sections"].get("Population", []), "population")

with tabs[2]:
    render_section_items("Housing", profile["sections"].get("Housing", []), "housing")

with tabs[3]:
    render_section_items("Salaries", profile["sections"].get("Salaries", []), "salaries")

with tabs[4]:
    render_section_items("Labour Market", profile["sections"].get("Labour Market", []), "labour")

with tabs[5]:
    section_header("Map view", "Commune-level metrics on a map of Luxembourg.")
    ranked = next(
        (item for item in profile["loaded_datasets"]
         if item.get("status") == "ready"
         and (item.get("rank") or {}).get("ranking") is not None),
        None,
    )
    if ranked is None:
        st.info("No commune-level ranking is available to place on a map yet.")
        render_map_empty_state()
    else:
        ranking = ranked["rank"]["ranking"]
        st.caption(f"Showing: {ranked['dataset'].title}")
        render_commune_map(
            ranking,
            name_col=ranking.columns[0],
            value_col=ranked["dataset"].value_column,
            title=ranked["dataset"].title,
        )

with tabs[6]:
    render_all_data_table(profile)
    commune_frames = [
        item["rows"].assign(DATASET_ID=item["dataset"].dataset_id, DATASET_TITLE=item["dataset"].title)
        for item in profile["loaded_datasets"]
        if item.get("status") == "ready" and not item.get("rows", pd.DataFrame()).empty
    ]
    if commune_frames:
        combined = pd.concat(commune_frames, ignore_index=True, sort=False)
        download_csv(combined, f"{profile['commune']}_all_commune_data.csv", "Download all available commune data")

with tabs[7]:
    section_header("Source details")
    source_rows = pd.DataFrame(profile["available_datasets"])
    if source_rows.empty:
        st.info("No source metadata is available yet.")
    else:
        st.dataframe(source_rows, use_container_width=True, hide_index=True)
    with st.expander("Caveats and TODOs", expanded=False):
        st.write(
            "Commune Portal only shows statistics from datasets declared or detected as commune-level. "
            "National-only datasets are intentionally excluded."
        )
        st.write(
            f"{profile['placeholder_count']} commune-level catalog entries are still placeholders and need exact STATEC / LUSTAT dataset IDs before they can show values."
        )
        st.write("The commune list is based on Luxembourg geoportal administrative commune metadata checked in May 2026.")

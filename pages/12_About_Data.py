from __future__ import annotations

import streamlit as st

from src.cache import list_cached_datasets
from src.ui.page_header import render_page_header
from src.ui.theme import section_header, trust_note
from src.ui_components import configure_page, render_sidebar

configure_page("LuxStats - About Data")
render_sidebar()

render_page_header("about", eyebrow="Help")

trust_note(
    "LuxStats turns official Luxembourg statistics into clear charts. Every number "
    "comes from STATEC / LUSTAT — the national statistics service. The app does not "
    "generate text, estimate missing values, or answer questions with AI.",
    heading="What LuxStats is",
)

# -- Where the data comes from --------------------------------------------
section_header("Where the data comes from")
st.write(
    "All figures are published by **STATEC**, Luxembourg's national statistics "
    "institute, through the **LUSTAT** open-data platform. LuxStats reads those "
    "official datasets, files and publication tables — nothing else."
)

# -- What the readiness labels mean ---------------------------------------
section_header("What “ready to chart” means")
st.write(
    "Not every official source can be charted safely straight away. LuxStats "
    "labels each one so you always know what you are looking at:"
)
st.markdown(
    "- **Ready to chart** — the source is mapped to a confirmed chart. This is "
    "what topic pages and search show first.\n"
    "- **Ready to preview** — the data is cached and can be shown as a table, "
    "but a chart still needs review.\n"
    "- **Needs mapping / review** — the source is official and relevant, but its "
    "columns or sheets must be confirmed before it can be charted.\n"
    "- **Download only** — the official file exists but is not table-shaped."
)
st.caption(
    "A source is only promoted to “ready to chart” when its mapping is explicit "
    "and verified — never guessed."
)

# -- Deterministic --------------------------------------------------------
section_header("Deterministic — no black box")
st.write(
    "“Deterministic” means the same data always produces the same charts and the "
    "same wording. Explanations are written in advance by people, not generated. "
    "There is no AI answer box and no invented insight."
)

# -- Freshness ------------------------------------------------------------
section_header("Freshness and caching")
st.write(
    "When you open a chart, LuxStats fetches the dataset from LUSTAT and caches it "
    "locally so it loads quickly next time. A “last refreshed” date shows when the "
    "data was cached on this deployment — it is not an official publication date."
)
with st.expander("Datasets cached on this deployment", expanded=False):
    cached = list_cached_datasets()
    if cached.empty:
        st.info("No datasets are cached yet. Open a chart to fetch its data.")
    else:
        st.dataframe(cached, use_container_width=True, hide_index=True)

# -- How to read a page ---------------------------------------------------
section_header("How to read a page")
st.markdown(
    "- Charts, plain-language explanations and a CSV download come first.\n"
    "- Technical detail — dataset IDs, columns, source links — stays inside "
    "“Advanced details” and “Source” expanders.\n"
    "- Official source links are always available so you can check the original."
)

st.divider()
st.caption(
    "Questions or corrections? LuxStats is open about its sources — start from the "
    "Source Library to inspect any official record."
)

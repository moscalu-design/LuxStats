# LuxStats Agent Instructions

LuxStats is a deterministic Streamlit portal for official Luxembourg statistics from STATEC / LUSTAT. Do not add any LLM, chatbot, GPT integration, AI answer box, model-backed planner, or generated statistical claim to the runtime.

## Product Goal

Make Luxembourg statistics fast and clear for normal people:

- search first
- charts immediately when mappings are confirmed
- official sources transparent
- raw details hidden under Advanced
- no fake data and no invented insights

## Architecture

- `app.py`: home entry point
- `pages/`: Streamlit pages
- `src/concepts.py`: curated chart-ready metric catalog
- `src/concept_view.py`: renders a curated chart block
- `src/topic_page.py`: topic dashboards
- `src/search.py`: plain-language search
- `src/data/source_catalog.py`: unified STATEC/LUSTAT source catalog
- `src/data/source_visualization.py`: source readiness index
- `src/ui/source_visualizer.py`: safe source viewer UI
- `src/ui/navigation.py`: grouped sidebar navigation
- `src/ui/page_header.py`: reusable page headers
- `src/ui/time_controls.py`: reusable period controls

## Source Mapping Rules

Use the source visualization index as the gatekeeper for what the UI can show.

Every source must be in one safe state:

- `chart_ready`
- `preview_ready`
- `downloadable_only`
- `needs_column_mapping`
- `needs_excel_inspection`
- `needs_manual_review`
- `not_chartable`
- `ignored_low_priority`

Only chart confirmed mappings. For new metrics, add a `Concept` or a reviewed Excel parser. Do not chart ambiguous data.

## Validation

Run:

```bash
python3 -m compileall app.py pages src tests scripts
.venv/bin/python -m pytest
./scripts/test_app.sh
```

If possible:

```bash
.venv/bin/streamlit run app.py
```

## Coding Standards

- Preserve working source/data logic.
- Keep advanced raw records behind expanders.
- Prefer reusable components over page-specific copies.
- Add tests for navigation, headers, source readiness, search ranking, and docs when touched.
- Do not remove user changes or unrelated work.

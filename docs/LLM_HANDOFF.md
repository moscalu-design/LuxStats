# LuxStats LLM Handoff

LuxStats is a deterministic Streamlit portal for official Luxembourg statistics from STATEC / LUSTAT. It must not include an LLM, chatbot, GPT integration, AI answer box, model-backed planner, or generated statistical claims.

## What Exists

- `app.py`: home page
- `pages/`: Streamlit pages
- `src/concepts.py`: curated chart-ready metrics
- `src/concept_view.py`: renders charts from concepts
- `src/topic_page.py`: topic dashboards
- `src/search.py`: plain-language search
- `src/data/source_catalog.py`: unified source library with 1,396 records
- `src/data/source_visualization.py`: readiness index for every source
- `src/ui/source_visualizer.py`: safe viewer for any source
- `src/ui/navigation.py`: grouped sidebar
- `src/ui/page_header.py`: page headers
- `src/ui/time_controls.py`: reusable time controls

## Source Rules

Every source should be quickly explorable through one safe state:

- chart-ready
- preview-ready
- downloadable only
- needs column mapping
- needs Excel inspection
- needs manual review
- not chartable
- low priority

Do not chart a source unless mapping is confirmed or safely implemented. For new public charts, add a curated `Concept` or reviewed Excel parser. Keep raw codes and tables under Advanced.

## Current Product Priorities

1. Housing prices, rents, construction, permits
2. Inflation, CPI, indexation, cost of living
3. Labour market, unemployment, jobseekers, vacancies
4. Population, migration, ageing, fertility, communes
5. Salaries, income, wage distribution, minimum wage
6. Economy, GDP, short-term indicators, confidence

## Validation

```bash
python3 -m compileall app.py pages src tests scripts
.venv/bin/python -m pytest
./scripts/test_app.sh
.venv/bin/streamlit run app.py
```

## Good Request Pattern

Ask for one scoped product outcome, name the page/module, require tests, and repeat: no fake data, no LLM runtime, official sources only.

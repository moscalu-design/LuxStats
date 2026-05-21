# LuxStats

LuxStats is a Streamlit portal for exploring official Luxembourg statistics from STATEC / LUSTAT. The goal is a friendly public data product: curated topic pages, simple filters, interactive Plotly charts, source notes, downloads, and a searchable dataset catalog.

The app is not centered on an LLM chatbot. The optional natural-language query tool from the original salary explorer is preserved inside the Salaries page, but the main product flow is dashboard and catalog driven.

## Current Structure

- `app.py` - main Streamlit entry page (the "find a statistic fast" home).
- `pages/` - Streamlit multipage topic dashboards.
- `src/concepts.py` - the curated concept layer: each entry maps an everyday
  question to a confirmed LUSTAT dataset plus chart configuration.
- `src/concept_view.py` - turns one concept into a finished, friendly chart
  block (metrics, chart, "what this means", source expander, CSV download).
- `src/topic_page.py` - renders a topic page from its curated concepts.
- `src/home.py` - home page: search box, topic cards, popular charts.
- `src/search.py` - synonym-aware search mapping plain words to concepts.
- `src/formatting.py` - human-friendly value/label formatting (euros, %, etc.).
- `src/charts.py` - reusable Plotly chart builders.
- `src/statec_client.py` - thin LUSTAT SDMX REST client.
- `src/cache.py` - CSV and DuckDB cache layer.
- `src/data_access.py` - high-level `get_dataset(id)` used by concepts.
- `src/catalog.py` - advanced dataset catalog with TODO entries for IDs that
  still need confirmation; powers the Dataset Explorer.
- `src/dashboard_specs.py` - catalog context for the Dataset Explorer.
- `src/transforms.py` - shared dataframe transformations.
- `src/ui_components.py` - shared Streamlit layout, theme, and source-info components.
- `src/salary_explorer.py` - advanced raw salary/dataflow explorer (opt-in).
- `data/cache/` - local DuckDB and CSV cache files.
- `data/metadata/` - place for curated metadata files as the catalog grows.

## UX Layers

- **Home** - large search box, topic cards, and one-click popular charts.
- **Search** - synonym-aware: "pay", "wages", "income" all find salary charts.
- **Topic pages** - Housing, Salaries, Population, Labour Market, Prices &
  Inflation each render their curated concepts as finished charts. No raw
  dataset IDs or SDMX jargon — those live inside each chart's advanced expander.
- **Dataset Explorer** - the advanced page for searching every official
  STATEC / LUSTAT dataset and exporting raw CSVs.

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Optional natural-language querying on the Salaries page uses:

```bash
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=...
```

If no key is set, the app falls back to a small deterministic planner.

## Deployment

This remains deployable on Streamlit Community Cloud:

1. Keep `app.py` at the repository root.
2. Keep dependencies in `requirements.txt`.
3. Add optional secrets in Streamlit Cloud if using the natural-language query expander.

Cached data is local to the running environment. Use the app's refresh buttons to update dataflow lists or selected datasets.

## Adding A Curated Chart

The fastest way to add a new statistic to a topic page is to add a `Concept`
to `src/concepts.py`:

1. Confirm the official LUSTAT dataflow ID against the live SDMX API or the
   Dataset Explorer. Only confirmed IDs belong in `concepts.py`.
2. Add a `Concept(...)` entry: friendly `title`, plain `description`, a
   matching `topic`, everyday `keywords`, the `dataset_id`, a `chart` type
   (`line` or `ranked_bar`), a `value_format`, and an `explanation`.
3. Set `series_dim`, `default_series`, `series_labels`, and `filters` so the
   chart shows the right, readable slice of the data.
4. Set `popular=True` to surface it on the home page. The topic page picks it
   up automatically via `concepts_for_topic(topic)`.

Unconfirmed candidate datasets stay in `src/catalog.py` with `TODO_CONFIRM_*`
IDs and power only the advanced Dataset Explorer. Do not invent dataset IDs.

Catalog entries should describe the dataset in normal language: title, theme, description, likely filters, geography, update frequency, dashboard fit, and caveats. The Dataset Explorer shows these fields before users need to inspect raw LUSTAT codes.
The catalog tests check that unconfirmed entries keep the `TODO_CONFIRM_*` prefix, themes match the app navigation, and placeholder dashboards have at least one matching catalog entry.

## Refreshing Data

- Dataflow list: use the refresh button in the Salaries page or Dataset Explorer.
- Dataset contents: open a dataset and click the fetch/refresh button.
- Cache location: `data/cache/lustat.duckdb` plus CSV files in `data/cache/csv/`.

## Tests

```bash
pytest
python -m py_compile app.py pages/*.py src/*.py tests/*.py
```

## Automated UX Refactor Loop

`run_codex_refactor_loop.sh` runs repeated Codex improvement cycles focused on UX/UI polish, commits each passing cycle, and pushes to GitHub by default so Streamlit Community Cloud can redeploy the connected branch.

```bash
STREAMLIT_APP_URL=https://your-app.streamlit.app ./run_codex_refactor_loop.sh
```

Useful controls:

- Stop after the current cycle: `touch STOP_AGENT`
- Run one cycle only: `MAX_CYCLES=1 SLEEP_SECONDS=0 ./run_codex_refactor_loop.sh`
- Disable pushing: `AUTO_PUSH=0 ./run_codex_refactor_loop.sh`
- Disable committing: `AUTO_COMMIT=0 ./run_codex_refactor_loop.sh`

The loop reads its UX instructions from `AGENT_TASK.md`. Keep that file focused on visible product improvements so the automation continues to prioritize the user experience over broad refactors.

## Roadmap

- Confirm official dataset IDs for rents, population by commune, education,
  mobility, and public finance, then add them as curated concepts.
- Add beginner-friendly in-page filters (year range, commune) to topic charts.
- Add richer metadata ingestion from LUSTAT structures where practical.
- Add map support after commune boundary data is selected and documented.

# LuxStats

LuxStats is a Streamlit portal for exploring official Luxembourg statistics from STATEC / LUSTAT. The goal is a friendly public data product: curated topic pages, simple filters, interactive Plotly charts, source notes, downloads, and a searchable dataset catalog.

The app is not centered on an LLM chatbot. The optional natural-language query tool from the original salary explorer is preserved inside the Salaries page, but the main product flow is dashboard and catalog driven.

## Current Structure

- `app.py` - main Streamlit entry page.
- `pages/` - Streamlit multipage dashboards.
- `src/statec_client.py` - thin LUSTAT SDMX REST client.
- `src/cache.py` - CSV and DuckDB cache layer.
- `src/catalog.py` - starter curated dataset catalog with TODO entries for IDs that still need confirmation.
- `src/dashboard_specs.py` - page-level placeholder copy and planned dashboard views.
- `src/charts.py` - reusable Plotly chart builders.
- `src/transforms.py` - shared dataframe transformations.
- `src/ui_components.py` - shared Streamlit layout and source-info components.
- `src/salary_explorer.py` - preserved and improved salary/dataflow explorer.
- `data/cache/` - local DuckDB and CSV cache files.
- `data/metadata/` - place for curated metadata files as the catalog grows.

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

## Adding A Dataset

1. Confirm the official LUSTAT dataflow ID from the Dataset Explorer or STATEC / LUSTAT.
2. Add or update an entry in `src/catalog.py`.
3. Include friendly keywords and aliases, such as `house prices`, `real estate`, `wages`, or `population by commune`.
4. For placeholder dashboards, add planned views in `src/dashboard_specs.py`.
5. Build a connected dashboard page using `get_dataset(dataset_id)` from `src/data_access.py`.
6. Show source details with `data_source_info(...)`.

Do not invent dataset IDs. Use `TODO_CONFIRM_*` placeholders until the official ID is verified.

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

## Roadmap

- Confirm official dataset IDs for housing, rents, population by commune, labour market, CPI, education, mobility, and public finance.
- Replace placeholder dashboard pages with curated filters and charts.
- Add richer metadata ingestion from LUSTAT structures where practical.
- Add map support after commune boundary data is selected and documented.

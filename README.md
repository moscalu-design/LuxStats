# LuxStats

LuxStats is a Streamlit portal that turns official Luxembourg statistics from
STATEC / LUSTAT into a **guided statistics product** — not just a prettier
dataset browser. Official LUSTAT data is powerful but dataset-first and
code-heavy. LuxStats answers human questions through clear UI flows instead:
*"What are housing prices doing?"*, *"How does my commune compare?"*,
*"What changed recently?"*

It is fully deterministic. **There is no LLM, chatbot, or AI answer box.**
Everything is driven by official data, curated metadata, reusable charts, and
static plain-language templates.

## What the app does

- **Find a Statistic** — search in plain language ("housing prices", "median
  salary", "population Hesperange") and get friendly metric cards.
- **Build a Chart** — pick a topic, metric, items and chart type in a few
  clicks; no dataset codes required.
- **Compare** — put communes head to head, or compare sectors and groups
  within one statistic.
- **What Changed?** — the latest available figures and the biggest recent
  moves, all calculated from real cached data.
- **Commune Portal** — choose one of Luxembourg's 100 communes and see every
  connected commune-level statistic in one profile, including a map view.
- **Topic dashboards** — Housing, Salaries, Population, Labour Market, Prices
  & Inflation, each rendered from curated charts with explanations and sources.
- **Dataset Explorer** — the advanced page for power users to search every
  official dataset and export raw CSVs.

Every chart shows a plain-language explanation, a source/freshness badge, and
a CSV download. Raw STATEC / LUSTAT codes stay inside "Advanced details"
expanders, hidden by default.

## Main user features

| Feature | Where |
| --- | --- |
| Metric Finder (friendly search) | Home, `pages/1_Find_a_Statistic.py` |
| Guided analysis cards | Home (`src/data/analysis_cards.py`) |
| Comparison mode | `pages/4_Compare.py` (`src/analysis/comparison.py`) |
| Build a Chart tool | `pages/2_Build_a_Chart.py` (`src/ui/chart_builder.py`) |
| What Changed page | `pages/5_What_Changed.py` (`src/analysis/changes.py`) |
| Commune Portal + map | `pages/3_Commune_Portal.py` |
| Plain-language explanations | `src/ui/explanations.py` |
| Source / freshness badges | `src/ui/source_badges.py` |

## Project structure

- `app.py` — Streamlit entry page (the product home).
- `pages/` — Streamlit multipage app, ordered for a product-led navigation.
- `src/concepts.py` — the **curated metric catalog**: each `Concept` maps an
  everyday question to a confirmed LUSTAT dataset plus chart configuration.
- `src/concept_view.py` — turns one concept into a finished chart block.
- `src/topic_page.py` — renders a topic dashboard from its concepts.
- `src/home.py` — home page sections: search, analysis cards, topic cards.
- `src/search.py` — synonym-aware search mapping plain words to concepts.
- `src/data/analysis_cards.py` — curated guided-analysis journey cards.
- `src/data/communes.py` — canonical commune names and cautious alias matching.
- `src/data/commune_portal.py` — defensive commune profile builder.
- `src/data/geography.py` — geospatial hook for commune boundary GeoJSON.
- `src/analysis/comparison.py` — metric and commune comparison engine.
- `src/analysis/changes.py` — recent-change detection.
- `src/ui/cards.py` — friendly metric and analysis cards.
- `src/ui/explanations.py` — template-based plain-language explanations.
- `src/ui/source_badges.py` — source and data-freshness badges.
- `src/ui/chart_builder.py` — the guided "Build a Chart" flow.
- `src/ui/maps.py` — commune map view (honest empty state until boundaries
  are connected).
- `src/ui/commune_components.py` — Commune Portal cards, charts, tables.
- `src/charts.py` / `src/formatting.py` — reusable Plotly charts and value
  formatting (euros, %, counts).
- `src/statec_client.py` / `src/cache.py` / `src/data_access.py` — LUSTAT
  SDMX client, DuckDB + CSV cache, and the high-level `get_dataset(id)`.
- `src/catalog.py` — advanced dataset catalog (includes `TODO_CONFIRM_*`
  placeholders) powering the Dataset Explorer.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Run the tests

```bash
python -m compileall app.py pages src tests
pytest
./scripts/test_app.sh
```

`scripts/test_app.sh` runs the compile check, pytest, a core Streamlit import
check, and optional Playwright browser tests when installed.

## How to add a new metric

Add a `Concept` to `src/concepts.py`:

1. Confirm the official LUSTAT dataflow ID against the live SDMX API or the
   Dataset Explorer. Only confirmed IDs belong in `concepts.py`.
2. Add a `Concept(...)`: friendly `title`, plain `description`, matching
   `topic`, everyday `keywords`, the `dataset_id`, a `chart` type (`line`,
   `ranked_bar`), a `value_format`, an `explanation`, and `geographic_level`.
3. Set `series_dim`, `default_series`, `series_labels`, `filters` so the chart
   shows the right, readable slice. A `series_dim` also makes the metric
   available in Compare and Build a Chart.
4. Set `popular=True` to surface it on the home page and What Changed.

The topic page, Metric Finder, chart builder and comparison engine all pick
the concept up automatically.

## How to add a new dataset

Unconfirmed candidate datasets stay in `src/catalog.py` as `CatalogEntry`
rows with `TODO_CONFIRM_*` IDs and `status="needs_confirmation"`; they power
only the advanced Dataset Explorer. Once an ID is confirmed, either promote it
to a `Concept` (for curated charts) or set `status="confirmed"` with a real
`dataset_id`. Never invent dataset IDs.

## How to add commune-level support

Add a confirmed commune-level `CatalogEntry` in `src/catalog.py`:

```python
CatalogEntry(
    dataset_id="CONFIRMED_LUSTAT_ID",
    theme="Population",
    title="Population by commune",
    friendly_title="Population by commune",
    description="Residents by commune and year.",
    geographic_level="commune",
    geography_column="COMMUNE_LABEL",
    commune_code_column="COMMUNE",
    commune_name_column="COMMUNE_LABEL",
    value_column="OBS_VALUE",
    time_column="TIME_PERIOD",
    commune_portal=True,
    status="confirmed",
)
```

`commune_portal=True` datasets appear in the Commune Portal, the commune
comparison mode, and the fastest-changing-communes ranking automatically.

## How to add a new analysis card

Add an `AnalysisCard` to `src/data/analysis_cards.py`. Each card needs a
`title`, plain `blurb`, `topic`, `difficulty`, `icon`, a `section`
(`popular` / `comparison` / `commune` / `changes`), and **either** a
`concept_id` (opens that chart inline) **or** a `page` path (routes there).
`card_validation_issues()` and the tests check that every card resolves.

## How to refresh data

- Dataflow list: refresh button in the Dataset Explorer.
- Dataset contents: open a dataset in the Dataset Explorer and fetch/refresh.
- Cache location: `data/cache/lustat.duckdb` plus CSVs in `data/cache/csv/`.

## Map views

Map views are deliberately honest: the app never fakes a map. Drop a commune
boundary GeoJSON at `data/geography/communes.geojson` (with a `name` property
per feature) and the Commune Portal map lights up automatically. Until then it
shows a clear "boundary data has not been connected" message.

## Deployment

Deployable on Streamlit Community Cloud with no changes:

1. Keep `app.py` at the repository root.
2. Keep dependencies in `requirements.txt`.

Cached data is local to the running environment; use the in-app refresh
buttons to update it.

## Known limitations / TODOs

- **Commune boundary GeoJSON is not bundled.** Map views show an honest empty
  state until `data/geography/communes.geojson` is connected. Official LAU
  commune boundaries are available from the Luxembourg geoportal /
  data.public.lu.
- **Several catalog datasets still need confirmed LUSTAT IDs** — rents,
  education, mobility, public finance and economy keep `TODO_CONFIRM_*`
  placeholders in `src/catalog.py` and are not charted.
- The housing commune metric (`DSD_CENSUS_NB_LOG_CLA@DF_B1707`) is a census
  **dwelling count**, not a rent or sale-price estimate. Confirmed
  commune-level rent / property-price tables should be added when available.
- "Recently updated" timestamps reflect when a dataset was last cached on the
  running deployment, not an official STATEC publication date.

## Dataset IDs / commune mappings to confirm manually

Confirmed commune-level LUSTAT tables wired into the Commune Portal:

- `DF_X021` — Population by canton and municipality.
- `DF_X020` — Population density by canton and municipality on 1 January.
- `DF_C1600` — Monthly salaries by municipality (Median indicator).
- `DF_X026` — Employment and unemployment by canton and municipality
  (unemployment-rate indicator).
- `DSD_CENSUS_NB_LOG_CLA@DF_B1707` — Census dwellings by canton and
  municipality (totals).
- `DSD_CENSUS_MENAGE_PV@DF_B1703` — Census private households by canton and
  municipality (total household size).

Still to confirm: official LUSTAT IDs for commune-level **rents** and
**sale prices**, **education**, **mobility**, **public finance**, and headline
**economy** indicators. The commune list is the 100 current Luxembourg
communes from Luxembourg geoportal administrative metadata (checked May 2026).

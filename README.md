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
- `src/data/categorization.py` — transparent keyword rules for categorizing
  any source into one of 20 themes and inferring its geographic level.
- `src/data/statec_api_catalog.py`, `statec_other_formats_catalog.py`,
  `statec_publication_catalog.py` — builders for the three source catalogs.
- `src/data/source_catalog.py` — the unified, searchable source catalog with
  priority scoring.
- `src/data/file_ingestion.py` — download and inspect Excel/CSV source files.
- `src/data/statec_web.py` — polite, domain-restricted page fetching.
- `src/ui/catalog_views.py` — catalog views embedded in product pages.
- `src/reports/source_catalog_report.py` — Markdown catalog report generator.
- `data/catalog/*.json` — committed source catalogs the app loads at runtime.
- `scripts/refresh_source_catalog.py`, `scripts/generate_source_report.py` —
  catalog maintenance (the only place crawling happens).

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

### STATEC publication Excel files

Some headline statistics — notably housing **sale prices** — are published by
STATEC as Excel workbooks rather than through the LUSTAT SDMX API.
`src/data/excel_sources.py` downloads and parses these into the same tidy
`TIME_PERIOD / OBS_VALUE / SPECIFICATION` shape, and `get_dataset()` routes any
dataset id prefixed `STATEC_XLS_` to it. A `Concept` then charts it like any
other. Currently wired: the D4011 house price index and average apartment
prices (publication *Logement en chiffres*).

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

## STATEC Source Catalog

Official Luxembourg statistics are scattered across three kinds of source.
The portal catalogs all of them into one searchable **unified source
catalog**, so users can find statistics without knowing where they live:

| Source type | What it is |
| --- | --- |
| `LUSTAT_API` | A dataflow in the LUSTAT SDMX API (machine-readable). |
| `STATEC_EXCEL` | An Excel/CSV table from STATEC's "data — other formats" pages. |
| `PUBLICATION_EXCEL` | An Excel annex attached to a STATEC publication. |
| `PUBLICATION_PDF` | A PDF report from a STATEC publication series. |
| `OTHER_FORMAT` | Any other downloadable file (zip, …). |

Every source is auto-categorized into 20 themes (Housing, Population,
Salaries / Income, …) by the transparent keyword rules in
`src/data/categorization.py`, given a geographic level, and scored for
ingestion priority (`high` / `medium` / `low`).

**The app only ever loads cached catalog JSON** from `data/catalog/` —
crawling never runs at page load. The catalog files are committed so the
deployed app has data. Browse everything on the **Source Library** page.

Modules: `src/data/statec_api_catalog.py` (LUSTAT API),
`statec_other_formats_catalog.py` (STATEC Excel tables),
`statec_publication_catalog.py` (publication annexes),
`source_catalog.py` (unified catalog + search + priority),
`file_ingestion.py` (download/inspect Excel files),
`statec_web.py` (polite, domain-restricted fetching).

### How to refresh the source catalog

```bash
python scripts/refresh_source_catalog.py          # uses page caches
python scripts/refresh_source_catalog.py --force  # re-download everything
```

This fetches the LUSTAT dataflow list and a small fixed set of official
STATEC pages (only `statistiques.public.lu`, `data.public.lu`,
`lustat.statec.lu`), rebuilds `data/catalog/*.json`, and is the only place
network crawling happens. Commit the updated `data/catalog/` files.

### How to generate the source report

```bash
python scripts/generate_source_report.py
```

Writes `reports/statec_source_catalog_report.md` — a breakdown of every
cataloged source by category, type, geographic level and priority, plus
recommended next sources to connect. Generated entirely from catalog data.

### How to inspect an Excel source

Open the **Source Library** page, filter to a `STATEC_EXCEL` or
`PUBLICATION_EXCEL` source, and use **Download / cache** then **Inspect
sheets**. Inspection reports sheet names, row counts, likely time / geography
/ value columns, and any detected commune names — and an ingestion status
(`cataloged` → `downloaded` → `inspected` → `importable` /
`needs_manual_mapping` / `failed`).

### How to add a manual mapping

Once an Excel/API source is confirmed useful, wire it into the curated layer:
add a `Concept` (`src/concepts.py`) for an API dataflow, or an entry in
`src/data/excel_sources.py` for an Excel file. The source catalog is for
*discovery*; the `Concept` layer is for *curated charts*.

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
- **Housing sale prices are national only.** The D4011 house price index and
  average apartment prices are connected (`src/data/excel_sources.py`), but
  STATEC publishes them at national level. Commune-level sale prices and
  **rents** are still not connected — add them when an official source is
  identified.
- The housing commune metric (`DSD_CENSUS_NB_LOG_CLA@DF_B1707`) is a census
  **dwelling count**, not a price estimate.
- Housing-price quarterly figures are averaged to a yearly value for the
  curated charts; the full quarterly detail is in each chart's advanced view.
- **Source categorization is heuristic.** ~25% of LUSTAT dataflows have terse
  titles and land in "Other / Unknown". Rules in `src/data/categorization.py`
  are deliberately transparent and easy to extend — improve them rather than
  hand-editing the catalog.
- The source catalog is a **discovery** layer: cataloged Excel/publication
  sources are not automatically charted. Connecting one still means adding a
  curated `Concept` or `excel_sources.py` entry (a manual mapping).
- The publication crawler covers a fixed set of well-known series. Add more
  slugs to `PUBLICATION_SERIES` in `src/data/statec_publication_catalog.py`.

## Next recommended ingestion priorities

`scripts/generate_source_report.py` ranks these from the live catalog. As of
the last refresh, the highest-value sources not yet wired into a curated
metric are commune-level Excel tables, housing indicators, and short-term
economic indicators — see section 11 of
`reports/statec_source_catalog_report.md`.
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

National housing **sale-price** data is sourced from the STATEC publication
*Logement en chiffres* (Excel file D4011): the house price index and average
apartment prices, quarterly from 2017.

Still to confirm: official sources for commune-level **rents** and
**sale prices**, **education**, **mobility**, **public finance**, and headline
**economy** indicators. The commune list is the 100 current Luxembourg
communes from Luxembourg geoportal administrative metadata (checked May 2026).

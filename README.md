# LuxStats — Current Situation

> This README is written as a copy/paste briefing for an LLM or new contributor.
> It describes **what the application is right now**, how it is built, what works,
> what is deployed, and what is still open. Snapshot date: **2026-05-22**.

---

## 1. What LuxStats is

LuxStats is a **Streamlit portal** that turns official Luxembourg statistics from
**STATEC / LUSTAT** into a guided statistics product — not a dataset browser.
Official LUSTAT data is powerful but dataset-first and code-heavy. LuxStats
answers human questions through clear UI flows instead: *"What are housing
prices doing?"*, *"How does my commune compare?"*, *"What changed recently?"*

**It is fully deterministic. There is no LLM, chatbot, or AI answer box at
runtime.** Everything is driven by official data, a curated metric catalog,
reusable Plotly charts, and static plain-language templates. Legacy
model-backed planner code has been removed from the runtime. (Note: the
`.env.example` file still mentions an `ANTHROPIC_API_KEY` for that old planner —
it is **stale**; the app requires no secrets and ignores it.)

This no-LLM-runtime rule is a hard product constraint. Do not add an LLM,
chatbot, GPT integration, AI answer box, model-backed planner, or generated
statistical claim to the runtime.

---

## 2. Current status

| Area | State |
| --- | --- |
| Code | Compiles cleanly (`compileall` on `app.py pages src tests scripts`). |
| Tests | **135 passed, 1 skipped** via `pytest`. |
| Git | Branch `main`, clean working tree, latest commit `a701e00`. |
| Remote | `github.com/moscalu-design/LuxStats`. |
| Deployment | Targets **Streamlit Community Cloud** (see §8). Repo is deploy-ready: `app.py` at root, `requirements.txt`, `.streamlit/config.toml` present. No secrets required. |
| Python | Local venv is 3.9; code targets 3.9+ and runs on Streamlit Cloud's default runtime. |

---

## 3. What the app does (user-facing)

- **Find a Statistic** — plain-language search ("housing prices", "median
  salary", "population Hesperange") returning friendly metric cards.
- **Build a Chart** — pick topic, metric, items and chart type in a few clicks;
  no dataset codes required.
- **Compare** — communes head to head, or sectors/groups within one statistic.
- **What Changed?** — latest available figures and biggest recent moves,
  computed from real cached data.
- **Commune Portal** — pick one of Luxembourg's 100 communes and see every
  connected commune-level statistic in one profile, including a map view.
- **Topic dashboards** — Housing, Salaries, Population, Labour Market, Prices &
  Inflation, Economy, Tourism. Topics with confirmed charts show charts first;
  topics still being mapped show source coverage without faking charts.
- **Source Library** — advanced inventory of all 1,396 official sources, with
  priority, mapping status and visualization readiness.
- **Dataset Explorer** — advanced page to search every LUSTAT API dataset and
  export raw CSVs.

Every chart shows a plain-language explanation, a source/freshness badge, and a
CSV download. Raw STATEC / LUSTAT codes stay inside "Advanced details"
expanders, hidden by default.

---

## 4. Navigation

The Streamlit sidebar is intentionally compact and product-led:

- **Main** — Home, Find a Statistic, Compare, Build a Chart, What Changed?
- **Topics** — Housing, Salaries & Income, Population, Labour Market, Prices &
  Inflation, Economy, Tourism.
- **Data & Sources** — Dataset Explorer and Source Library (advanced
  inspection areas).
- **About / Help** — About Data.

The Commune Portal is reachable from Home, search results, source actions, and
commune-focused cards, but it is not a top-level sidebar item.

### Pages (`pages/`)

`1_Find_a_Statistic`, `2_Build_a_Chart`, `3_Commune_Portal`, `4_Compare`,
`5_What_Changed`, `6_Housing`, `7_Salaries`, `8_Population`, `9_Labour_Market`,
`10_Prices_Inflation`, `11_Dataset_Explorer`, `12_About_Data`,
`13_Source_Library`, `14_Economy`, `15_Tourism`.

---

## 5. Data model & current numbers

### Curated layer (the product front door)

- **`src/concepts.py`** — the curated metric catalog: **25 `Concept` entries**.
  Each `Concept` maps an everyday question to a confirmed LUSTAT dataset plus
  chart configuration (chart type, value format, explanation, series).
- Concepts span **7 topics**: Housing, Salaries, Population, Labour Market,
  Prices & Inflation, Economy, Tourism.
- `src/concept_view.py` renders one concept into a finished chart block;
  `src/topic_page.py` renders a topic dashboard from its concepts.

### Source catalog (the discovery layer)

The unified source catalog (`data/catalog/unified_source_catalog.json`) holds
**1,396 official sources**, committed so the deployed app has data without
crawling. By source type:

| Source type | Count | What it is |
| --- | --- | --- |
| `LUSTAT_API` | 904 | Dataflows in the LUSTAT SDMX API. |
| `PUBLICATION_PDF` | 451 | PDF reports from STATEC publication series. |
| `STATEC_EXCEL` | 38 | Excel/CSV tables from STATEC "other formats" pages. |
| `PUBLICATION_EXCEL` | 3 | Excel annexes attached to STATEC publications. |

### Visualization readiness index

`data/catalog/source_visualization_index.json` classifies every source into the
safest available UX. Current breakdown of all 1,396 sources:

| `visualization_status` | Count | Meaning |
| --- | --- | --- |
| `chart_ready` | 28 | Confirmed chart/profile route exists. |
| `needs_column_mapping` | 600 | API data exists; columns/filters need confirmation. |
| `needs_manual_review` | 451 | Usually PDF/publication material needing human review. |
| `ignored_low_priority` | 282 | Official but not a current public priority. |
| `needs_excel_inspection` | 35 | Excel/CSV source should be downloaded and inspected. |

(`preview_ready`, `downloadable_only` and `not_chartable` are also valid states
but have no current members.)

Mapping status (`src/data/source_mapping.py`) is a parallel classification:
`mapped_to_metric`, `mapped_to_commune_portal`, `unmapped`,
`needs_manual_review`, `ignored_low_priority`.

**The app only ever loads cached catalog JSON from `data/catalog/`** — crawling
never happens at page load.

---

## 6. Architecture

```
app.py                  Streamlit entry page → src/home.render_home()
pages/                   15 Streamlit pages (product-led order)
.streamlit/config.toml   Theme + headless server config
data/catalog/*.json      Committed source catalogs loaded at runtime
data/cache/              Local DuckDB + CSV cache (per-environment, not committed)
```

### `src/` modules

**Curated charts**
- `concepts.py` — curated chart-ready metric catalog (25 Concepts).
- `concept_view.py` — renders one concept into a chart block.
- `topic_page.py` — renders a topic dashboard from concepts.
- `home.py` — home sections: search, analysis cards, topic cards.
- `search.py` — synonym-aware plain-language search → concepts.
- `charts.py` / `formatting.py` — reusable Plotly charts & value formatting.

**Data access**
- `statec_client.py` — LUSTAT SDMX client.
- `cache.py` — DuckDB + CSV cache.
- `data_access.py` — high-level `get_dataset(id)`; routes `STATEC_XLS_*` ids to
  Excel parsers.
- `catalog.py` — advanced dataset catalog (includes `TODO_CONFIRM_*`
  placeholders) powering the Dataset Explorer.

**Source catalog & readiness** (`src/data/`)
- `source_catalog.py` — unified searchable catalog + priority scoring.
- `statec_api_catalog.py`, `statec_other_formats_catalog.py`,
  `statec_publication_catalog.py` — builders for the three source catalogs.
- `source_mapping.py` — derived mapping status.
- `source_visualization.py` — readiness state for every source.
- `categorization.py` — transparent keyword rules: 20 themes + geo level.
- `file_ingestion.py` — download/inspect Excel/CSV files.
- `statec_web.py` — polite, domain-restricted page fetching.
- `excel_sources.py` — parses STATEC publication Excel workbooks.
- `analysis_cards.py` — curated guided-analysis journey cards.
- `priority_topics.py` — public-interest priority topics & question cards.
- `time_utils.py` — annual/quarterly/monthly/date period parsing.
- `communes.py` — canonical commune names + cautious alias matching.
- `commune_portal.py` — defensive commune profile builder.
- `geography.py` — geospatial hook for commune boundary GeoJSON.

**Analysis** (`src/analysis/`)
- `comparison.py` — metric and commune comparison engine.
- `changes.py` — recent-change detection.

**UI** (`src/ui/`)
- `cards.py`, `explanations.py`, `source_badges.py`, `chart_builder.py`,
  `time_controls.py`, `navigation.py`, `page_header.py`, `source_visualizer.py`,
  `maps.py`, `commune_components.py`, `catalog_views.py`.

**Reports** (`src/reports/`)
- `source_catalog_report.py` — Markdown catalog report generator.

### Scripts (`scripts/`)
- `refresh_source_catalog.py` — the only place network crawling happens.
- `generate_source_report.py` — writes the catalog breakdown report.
- `build_source_visualization_index.py` — rebuilds the readiness index.
- `test_app.sh` — compile check + pytest + import check + optional Playwright.

---

## 7. Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Dependencies (`requirements.txt`): `streamlit`, `duckdb`, `pandas`, `requests`,
`plotly`, `xlrd`, `openpyxl`, `python-dotenv`, `pytest`. No API keys needed.

### Validate

```bash
python3 -m compileall app.py pages src tests scripts
.venv/bin/python -m pytest
./scripts/test_app.sh
```

---

## 8. Deployment

The app deploys to **Streamlit Community Cloud** with no code changes.

1. Go to **share.streamlit.io**, sign in with a GitHub account with access to
   `moscalu-design/LuxStats`.
2. **Create app → Deploy a public app from GitHub**.
3. Repository `moscalu-design/LuxStats`, branch `main`, main file `app.py`.
4. **Secrets:** leave empty — none required.
5. Deploy. Every push to `main` then auto-redeploys.

Cached data (`data/cache/`) is local to the running environment; use the in-app
refresh buttons (Dataset Explorer) to update it. The committed
`data/catalog/*.json` files mean the deployed app has source data immediately.

---

## 9. Known limitations / open work

- **Commune boundary GeoJSON is not bundled.** Map views show an honest empty
  state until `data/geography/communes.geojson` (with a `name` property per
  feature) is added. Official LAU boundaries are on the Luxembourg geoportal /
  data.public.lu.
- **Several catalog datasets still lack confirmed LUSTAT IDs** — rents,
  education, mobility, public finance, economy keep `TODO_CONFIRM_*`
  placeholders in `src/catalog.py` and are not charted.
- **Housing sale prices are national only.** The D4011 house price index and
  average apartment prices are connected via `src/data/excel_sources.py`, but
  STATEC publishes them at national level. **Commune-level sale prices and
  rents are still not connected.**
- The housing commune metric `DSD_CENSUS_NB_LOG_CLA@DF_B1707` is a census
  **dwelling count**, not a price estimate.
- Housing-price quarterly figures are averaged to yearly for curated charts;
  full quarterly detail is in each chart's advanced view.
- **Source categorization is heuristic.** ~25% of LUSTAT dataflows have terse
  titles and land in "Other / Unknown". Improve rules in
  `src/data/categorization.py` rather than hand-editing the catalog.
- "Recently updated" timestamps reflect when a dataset was last cached on the
  running deployment, not an official STATEC publication date.
- The publication crawler covers a fixed set of series; add slugs to
  `PUBLICATION_SERIES` in `src/data/statec_publication_catalog.py`.

### Next recommended ingestion priorities

See `reports/source_mapping_priorities.md`. Highest-value unmapped items:
housing permits by canton, population census breakdowns by commune, fertility,
and short-term economy indicators.

### Confirmed commune-level LUSTAT tables (wired into the Commune Portal)

- `DF_X021` — Population by canton and municipality.
- `DF_X020` — Population density by canton and municipality on 1 January.
- `DF_C1600` — Monthly salaries by municipality (Median).
- `DF_X026` — Employment/unemployment by canton and municipality.
- `DSD_CENSUS_NB_LOG_CLA@DF_B1707` — Census dwellings by commune.
- `DSD_CENSUS_MENAGE_PV@DF_B1703` — Census private households by commune.

---

## 10. Extending the app

- **New metric** → add a `Concept` to `src/concepts.py` (confirmed LUSTAT
  dataflow ID, friendly title, topic, keywords, chart type, value format,
  explanation, `series_dim`/`filters`). Set `popular=True` to surface it on
  Home and What Changed. Topic page, Metric Finder, chart builder and Compare
  pick it up automatically.
- **New candidate dataset** → add a `CatalogEntry` to `src/catalog.py` with a
  `TODO_CONFIRM_*` id and `status="needs_confirmation"`. Never invent dataset
  IDs. Promote to a `Concept` once confirmed.
- **STATEC publication Excel** → add a parser in `src/data/excel_sources.py`;
  `get_dataset()` routes `STATEC_XLS_*` ids to it.
- **Commune-level dataset** → add a confirmed `CatalogEntry` with
  `commune_portal=True` and the commune/value/time columns set.
- **Analysis card** → add an `AnalysisCard` to `src/data/analysis_cards.py`
  (title, blurb, topic, difficulty, icon, section, and either `concept_id` or
  `page`). `card_validation_issues()` and tests verify every card resolves.

Rules: only chart confirmed mappings; never fake data or invent insights; keep
raw codes/tables behind Advanced expanders; preserve the no-LLM-runtime rule;
run validation before summarizing.

---

## 11. Refreshing data & reports

```bash
python scripts/refresh_source_catalog.py          # rebuild data/catalog/*.json (uses page caches)
python scripts/refresh_source_catalog.py --force  # re-download everything
python scripts/build_source_visualization_index.py # rebuild the readiness index
python scripts/generate_source_report.py           # rebuild the catalog report
```

`refresh_source_catalog.py` is the only place network crawling happens; it only
touches `statistiques.public.lu`, `data.public.lu`, `lustat.statec.lu`. Commit
updated `data/catalog/` files afterward.

Reports in `reports/`: `statec_source_catalog_report.md`,
`production_readiness_review.md`, `screen_by_screen_ux_audit.md`,
`source_visualization_index.md`, `source_mapping_priorities.md`.

---

## 12. Working with an LLM / coding agent

Checked-in handoff files (keep them and this README in sync):

- `AGENTS.md` — shared rules for coding agents.
- `CLAUDE.md` — Claude Code-specific notes.
- `CODEX.md` — Codex-specific notes.
- `docs/LLM_HANDOFF.md` — concise copy/paste context.
- `docs/PROMPTING_GUIDE.md` — prompt examples for common tasks.

Any future agent must preserve the no-LLM-runtime rule and validate with the
commands in §7.

# Production Readiness Review

Review date: 2026-05-21

## 1. Summary of App State

LuxStats is now a deterministic Streamlit portal over official STATEC/LUSTAT data. It has curated metric cards, topic pages, a Commune Portal, Compare, Build a Chart, What Changed, Dataset Explorer, and a Source Library covering 1,396 cataloged official sources.

The core product risk was source-library overload: the app had enough official inventory to become a prettier raw catalog. The production pass focused on making the source catalog power better entry points while keeping raw source tools under Advanced.

The app remains model-free. A legacy advanced salary-query path that could call an external planner was removed from the runtime and replaced with explicit deterministic grouping controls.

Second pass update: the app now has a source visualization readiness index for all 1,396 cataloged sources, centralized navigation, centralized page headers, and a Source Library viewer that gives every source a safe next action.

## 2. Major UX Issues Found

- Home page relied on curated journey cards but did not clearly expose source-backed question coverage.
- Metric Finder showed raw source fallbacks, but not as a clearly lower-priority group.
- Source Library opened as a large advanced table without enough mapping/readiness context.
- Time controls were inconsistent: curated charts, Compare, Build a Chart, and Commune Portal used different period UI patterns.
- Economy had source coverage but no user-facing topic page.
- Commune Portal had data and map views but no clear compare call-to-action.
- Dataset Explorer and Source Library overlapped in wording; Dataset Explorer needed clearer “advanced API inspector” positioning.
- Legacy salary explorer copy and dependencies still suggested a model-backed query path, which conflicted with the deterministic product requirement.

## 3. Navigation Changes Made

- Sidebar topic labels were clarified, including “Salaries & income.”
- Advanced tools are now grouped under “Advanced.”
- Economy was added as a topic page backed by source coverage, not fake charts.
- Dataset Explorer copy now distinguishes it from Source Library.
- Advanced salary exploration now uses explicit grouping, aggregation, chart and export controls instead of natural-language planning.
- Added `src/ui/navigation.py` and `src/ui/page_header.py` so sidebar labels and page headers are consistent.

## 4. Source Library Integration Changes

- Added derived mapping status:
  - `mapped_to_metric`
  - `mapped_to_commune_portal`
  - `unmapped`
  - `needs_manual_review`
  - `ignored_low_priority`
- Added chart-ready and commune-ready flags.
- Added Source Library readiness metrics.
- Added mapping-status filter.
- Added “Recommended next mappings” section.
- Added reusable source-coverage badges for Home, Metric Finder, topic pages, Commune Portal, and What Changed.
- Added `src/data/source_visualization.py` and `src/ui/source_visualizer.py`.
- Generated `data/catalog/source_visualization_index.json`.
- Current readiness counts: 13 chart-ready, 0 preview-ready, 650 needing mapping or Excel inspection, 451 needing manual review, 282 low-priority.

## 5. Home Page Improvements

- Added source-backed question cards ordered by public-interest priority and chart readiness.
- Cards now show source counts and mapping status.
- Added a commune quick-search panel.
- Added a product-readiness coverage block so the catalog feels useful, not overwhelming.
- Added a direct “Visualize or inspect any source” shortcut.

## 6. Time-Scale and Chart-Control Improvements

- Added reusable period parsing in `src/data/time_utils.py`.
- Added reusable Streamlit controls in `src/ui/time_controls.py`.
- Supported annual, quarterly, monthly, date-like, and common STATEC period codes.
- Wired time controls into:
  - curated metric charts
  - Build a Chart
  - Compare
  - Commune Portal trend charts
  - Dataset Explorer API preview charts
  - What Changed commune movement calculations
- Empty period ranges now show friendly messages.

## 7. Pages Reviewed

- Home
- Find a Statistic
- Build a Chart
- Commune Portal
- Compare
- What Changed
- Housing
- Salaries
- Population
- Labour Market
- Prices & Inflation
- Economy
- Dataset Explorer
- Source Library
- About the Data

## 8. Bugs Fixed

- Playwright search test had an ambiguous `Hesperange` locator; it now targets the commune profile heading.
- Dataset Explorer copy was clarified to reduce duplicate-purpose confusion.
- Topic pages with source coverage but no chart-ready concepts now show source coverage and mapped/unmapped context instead of a dead-end message.
- Removed the model planner runtime dependency and added a regression test that prevents reintroducing Anthropic/OpenAI runtime requirements.
- Replaced raw exception text in advanced download/fetch failures with friendly messages and hidden technical details.
- Reworked Source Library from table-first catalog to readiness summary, queues, filters, paginated tables and universal source viewer.

## 9. Remaining Risks

- Only a small subset of the 1,396 sources are mapped to beginner charts.
- Some publication annexes require manual review before safe ingestion.
- Quarterly housing sources are currently simplified into yearly concept views; deeper quarterly UX should be added next.
- Economy has source coverage but still lacks chart-ready curated metrics.
- Some source categories remain “Other / Unknown” and need categorization refinement.

## 10. Recommended Next Work

1. Map housing permits by canton/region from `DF_D4113`.
2. Add fertility and age-structure charts from population sources.
3. Add a clean Economy starter metric from short-term indicators.
4. Add CPI category/component charts and indexation context using official STATEC publications.
5. Add jobseekers/vacancies by category if the official source maps cleanly.
6. Continue reducing raw table exposure in advanced pages by adding previews, summaries, and “show more” controls.
7. Add deep links to specific Source Library records so search results can open the exact selected source.

Public-interest priority inputs checked during this pass included STATEC's February 2026 inflation forecast and indexation note, March 2026 Conjoncture Flash, the March 2026 Logement en chiffres item, and May 2026 reporting on population growth driven by migration. These inputs only informed ordering and question-card priorities; no news content is ingested as statistics.

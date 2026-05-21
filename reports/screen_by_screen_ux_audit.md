# Screen-by-Screen UX Audit

Review date: 2026-05-21

## Home

- Current purpose: front door for search, popular questions, topics, communes, updates, and coverage.
- UX issues found: header was hero-like but inconsistent with other pages; source coverage did not explain readiness states clearly enough.
- Fixes implemented: added reusable page header, source-backed search fallbacks, and a clear Source Library readiness shortcut.
- Remaining TODOs: add richer What Changed preview once more high-priority datasets are cached.

## Find a Statistic

- Current purpose: plain-language search across metrics, communes, and official sources.
- UX issues found: source fallbacks were separate raw catalog records, not ranked by visualization usefulness.
- Fixes implemented: added readiness-index search so chart-ready and preview-ready sources rank ahead of unmapped/raw records.
- Remaining TODOs: add direct deep-linking into a selected Source Library record.

## Commune Portal

- Current purpose: one commune profile with mapped local datasets.
- UX issues found: header copy was separate from the rest of the app; local source details were useful but advanced.
- Fixes implemented: standardized header and preserved tabs, coverage, Compare action, downloads, and collapsed source details.
- Remaining TODOs: add commune boundary GeoJSON and map styling once official boundaries are connected.

## Compare

- Current purpose: compare communes or groups within chart-ready metrics.
- UX issues found: title was less specific than the actual task.
- Fixes implemented: standardized header as “Compare Statistics”; kept time controls and source details.
- Remaining TODOs: add more comparable metrics as source mappings grow.

## Build a Chart

- Current purpose: guided chart builder for official chart-ready metrics.
- UX issues found: only curated concepts were visible; the source library did not feed advanced chart-ready choices.
- Fixes implemented: added Beginner/Advanced mode. Advanced mode uses chart-ready visualization-index entries only and shows mapping-needed sources separately.
- Remaining TODOs: support non-concept chart-ready mappings if future mappers create them.

## What Changed?

- Current purpose: recent metric updates, movers, topic watch lists, and publication sources.
- UX issues found: commune change ranking lacked a visible time-range control.
- Fixes implemented: added reusable time controls before commune change calculations and standardized header.
- Remaining TODOs: add official publication-date ordering for more source families.

## Housing

- Current purpose: curated housing charts plus official source context.
- UX issues found: source catalog appeared only as a collapsed list, not as readiness-aware mapping guidance.
- Fixes implemented: topic page now shows chart-ready source mappings and unmapped source queues from the readiness index.
- Remaining TODOs: map building permits by canton and improve quarterly housing views.

## Salaries & Income

- Current purpose: salary charts and optional advanced salary dataset exploration.
- UX issues found: advanced explorer previously suggested natural-language planning.
- Fixes implemented: advanced explorer is deterministic with explicit grouping/query controls; standardized topic header.
- Remaining TODOs: map income distribution sources if clean official mappings are confirmed.

## Population

- Current purpose: population chart and official source context.
- UX issues found: many relevant population sources existed but were not surfaced as mapping tasks.
- Fixes implemented: readiness-aware “sources available but not mapped yet” section.
- Remaining TODOs: map fertility, age structure, migration, and commune population breakdowns.

## Labour Market

- Current purpose: jobs/unemployment charts and source context.
- UX issues found: jobseeker/vacancy source availability was not obvious.
- Fixes implemented: topic page uses readiness-index queues.
- Remaining TODOs: map jobseekers/vacancies by category if source dimensions are clean.

## Prices & Inflation

- Current purpose: CPI and inflation charts with source context.
- UX issues found: CPI/indexation-related sources were not surfaced as next mapping opportunities.
- Fixes implemented: topic page readiness sections now expose mapped/unmapped sources.
- Remaining TODOs: add CPI component and indexation context from official STATEC sources.

## Economy

- Current purpose: source-backed placeholder topic until safe chart mappings exist.
- UX issues found: no chart-ready economy metrics yet.
- Fixes implemented: standardized header and readiness-aware source coverage.
- Remaining TODOs: map one starter GDP/short-term indicator metric.

## Dataset Explorer

- Current purpose: inspect concrete chart-ready/API datasets in detail.
- UX issues found: it overlapped conceptually with Source Library and charts lacked consistent period controls.
- Fixes implemented: clarified page distinction and added time controls to API preview charts.
- Remaining TODOs: cross-link selected source IDs from Source Library.

## Source Library

- Current purpose: advanced official source inventory and mapping/readiness workspace.
- UX issues found: default was too table-first for 1,396 records and did not clearly answer “what can I do with this source?”
- Fixes implemented: added visualization readiness summary, quick filters, chart-ready queue, mapping queue, readiness filters, source actions, and universal source viewer.
- Remaining TODOs: add URL/query deep links for selected sources and richer Excel inspection caching.

## About the Data

- Current purpose: explain data sources, cache, and how to read pages.
- UX issues found: title/header did not match the rest of the app.
- Fixes implemented: standardized header.
- Remaining TODOs: add a short diagram of source catalog -> readiness index -> curated concepts.

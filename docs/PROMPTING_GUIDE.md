# LuxStats Prompting Guide

Use these prompts with Claude, ChatGPT, or Codex when returning to LuxStats.

## Screen-by-Screen UX Pass

Review every Streamlit page as a public user. Identify confusing navigation, generic headers, table-first flows, missing empty states, and source-library overload. Fix scoped issues, update `reports/screen_by_screen_ux_audit.md`, and run tests. Do not add LLM features or fake data.

## Add a New Metric

Map one confirmed official STATEC/LUSTAT source into a curated `Concept`. Confirm dataset ID, choose safe filters, add plain labels, add time controls, add source details, and add tests. If mapping is ambiguous, stop at `needs_column_mapping`.

## Map a Source

Use `src/data/source_visualization.py` and Source Library readiness status. Inspect the source, decide whether it is chart-ready, preview-ready, needs Excel inspection, needs manual review, or low priority. Do not chart PDFs or ambiguous sheets.

## Improve a Topic Page

Make the topic page answer human questions first. Show curated charts, source coverage, chart-ready source mappings, and collapsed unmapped sources. Avoid giant raw tables.

## Fix Chart Time Controls

Use `src/data/time_utils.py` and `src/ui/time_controls.py`. Support annual, quarterly, monthly, and date-like periods. Preserve friendly labels and show empty states for invalid ranges.

## Improve Source Library

Do not render all 1,396 sources as cards. Use readiness summary, search, filters, pagination, source cards, and the universal source viewer. Every source needs a clear next action.

## Debug Deployment

Run compile, pytest, `scripts/test_app.sh`, then `streamlit run app.py`. Keep Streamlit Cloud compatibility and avoid network refreshes on app load.

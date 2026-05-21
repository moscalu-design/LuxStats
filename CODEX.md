# Codex Notes

Use `AGENTS.md` as the shared source of truth.

Recommended workflow:

1. Read the page, shared helper, and tests that touch the request.
2. For UX passes, create or update `reports/screen_by_screen_ux_audit.md`.
3. Prefer centralized helpers:
   - navigation: `src/ui/navigation.py`
   - headers: `src/ui/page_header.py`
   - source readiness: `src/data/source_visualization.py`
   - source viewer: `src/ui/source_visualizer.py`
4. Never fabricate data or silently infer a chart from an unmapped source.
5. Use `apply_patch` for manual edits.
6. Run validation and report exact outcomes.

Do not reintroduce:

- `anthropic`
- `openai`
- chatbot UI
- model-backed query planners
- fake chart values

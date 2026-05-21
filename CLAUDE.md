# Claude Code Notes

Use `AGENTS.md` as the shared source of truth.

When working on LuxStats:

1. Inspect the relevant page/component before editing.
2. Keep changes scoped and product-led.
3. Do not add LLM/runtime model features.
4. Use the source visualization index to decide whether a source can be charted.
5. If a source is ambiguous, mark it as needing mapping or manual review.
6. Run validation before summarizing.

Useful commands:

```bash
python3 -m compileall app.py pages src tests scripts
.venv/bin/python -m pytest
./scripts/test_app.sh
.venv/bin/python scripts/build_source_visualization_index.py
```

Summaries should state:

- user-facing UX changes
- data/source mapping changes
- tests run
- remaining mapping risks

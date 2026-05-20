Continue improving the LuxStats Streamlit app as a friendly Luxembourg statistics portal.

Work incrementally and keep the app deployable on Streamlit Community Cloud.

Priorities:
- Preserve the existing salary explorer and LUSTAT dataflow functionality.
- Improve modularity, catalog metadata, dashboard placeholders, documentation, tests, and defensive error handling.
- Do not invent official dataset IDs. Use TODO_CONFIRM_* placeholders until IDs are verified from LUSTAT.
- Keep the LLM query feature optional and secondary.
- Avoid unrelated rewrites and avoid deleting working features.

Before finishing each cycle:
- Run syntax checks and the available tests when practical.
- Summarize changed files and any remaining TODOs.

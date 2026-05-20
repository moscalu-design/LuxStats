Continue improving the LuxStats Streamlit app as a friendly Luxembourg statistics portal with a strong UX/UI and engagement focus.

Work incrementally and keep the app deployable on Streamlit Community Cloud.

Priorities:
- Preserve the existing salary explorer and LUSTAT dataflow functionality.
- Make the app feel more polished, friendly, and useful for regular people exploring Luxembourg statistics.
- Improve navigation, page hierarchy, chart presentation, empty states, source/caveat panels, explanatory copy, mobile readability, and visual consistency.
- Prefer concrete visible UX improvements over invisible refactors.
- Keep each cycle small enough to review: one coherent UX/UI improvement, plus any needed tests/docs.
- Do not invent official dataset IDs. Use TODO_CONFIRM_* placeholders until IDs are verified from LUSTAT.
- Keep the LLM query feature optional and secondary.
- Avoid unrelated rewrites and avoid deleting working features.
- Avoid adding fake data. Placeholder dashboard content must clearly say what still needs confirmed LUSTAT data.

Before finishing each cycle:
- Run syntax checks and the available tests when practical.
- Confirm the Streamlit app remains deployable from `app.py`.
- Summarize changed files and any remaining TODOs.

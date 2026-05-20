"""Natural-language → structured query plan.

The LLM is instructed to emit ONLY a JSON plan with the shape that
``analytics.execute_plan`` understands. It never does arithmetic on the data.
If no API key is configured, a tiny heuristic planner produces a reasonable
default plan so the app still works offline.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

SYSTEM_PROMPT = """\
You translate a user's natural-language question about a Luxembourg statistics
dataset into a STRICT JSON query plan. You never perform calculations and you
never produce SQL — Python/DuckDB executes the plan.

Output rules:
1. Output a single JSON object and NOTHING else (no prose, no markdown).
2. Use only column names that appear in the provided schema (case-sensitive).
3. Filter values must come from the listed sample values when possible.

Plan schema:
{
  "filters":     { "<COLUMN>": <string|number> | [<string|number>, ...] | {"min": .., "max": ..} },
  "dimensions":  ["<COLUMN>", ...],         // GROUP BY columns
  "measures":    ["<COLUMN>", ...],         // usually ["OBS_VALUE"]
  "aggregation": "sum"|"avg"|"min"|"max"|"count"|"median"|"none",
  "sort":        [{"column": "<COLUMN>", "order": "asc"|"desc"}, ...],
  "limit":       <int|null>,
  "chart": {
    "type": "line"|"bar"|"table",
    "x": "<COLUMN>",
    "y": "<COLUMN>",
    "color": "<COLUMN>"|null
  },
  "explanation": "one short sentence describing what this plan computes"
}

Conventions:
- For "trend over time" questions, dimensions should include TIME_PERIOD and chart.type = "line".
- For comparisons across categories, chart.type = "bar".
- If the user does not specify, default aggregation to "avg" on OBS_VALUE grouped by TIME_PERIOD.
- If you cannot answer with the schema, return a plan with "explanation" describing the gap.
"""


def _heuristic_plan(question: str, schema: dict[str, Any]) -> dict[str, Any]:
    cols = [c["name"] for c in schema.get("columns", [])]
    col_set = set(cols)
    plan: dict[str, Any] = {
        "filters": {},
        "dimensions": [],
        "measures": ["OBS_VALUE"] if "OBS_VALUE" in col_set else [],
        "aggregation": "avg",
        "sort": [],
        "limit": 500,
        "chart": {"type": "line", "x": None, "y": "OBS_VALUE", "color": None},
        "explanation": "Heuristic plan (no LLM configured): average OBS_VALUE over time.",
    }
    if "TIME_PERIOD" in col_set:
        plan["dimensions"].append("TIME_PERIOD")
        plan["chart"]["x"] = "TIME_PERIOD"
        plan["sort"].append({"column": "TIME_PERIOD", "order": "asc"})
    q_lower = question.lower()
    for hint in ("SEX", "GENDER", "SEXE"):
        if hint in col_set and any(t in q_lower for t in ("gender", "sex", "men", "women", "male", "female")):
            plan["dimensions"].append(hint)
            plan["chart"]["color"] = hint
            break
    return plan


def _call_anthropic(question: str, schema: dict[str, Any]) -> dict[str, Any] | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
    except ImportError:
        return None
    client = anthropic.Anthropic(api_key=api_key)
    user_msg = (
        "Dataset schema:\n"
        + json.dumps(schema, ensure_ascii=False)
        + "\n\nUser question: "
        + question.strip()
        + "\n\nReturn ONLY the JSON plan."
    )
    model = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-7")
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = "".join(
        block.text for block in resp.content if getattr(block, "type", None) == "text"
    )
    return _extract_json(text)


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


def plan_query(question: str, schema: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """Return (plan, source) where source is "llm" or "heuristic"."""
    plan = _call_anthropic(question, schema)
    if plan is not None:
        return plan, "llm"
    return _heuristic_plan(question, schema), "heuristic"

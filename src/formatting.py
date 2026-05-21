"""Human-friendly value and label formatting.

These helpers keep numbers readable for non-technical visitors: euros look
like euros, percentages look like percentages, big counts get thousands
separators, and raw STATEC column codes get plain-language names.
"""

from __future__ import annotations

import math

# How each value format should be displayed and how Plotly axes/hovers format it.
VALUE_FORMATS = {
    "number": {"suffix": "", "prefix": "", "decimals": 0, "tick": ",.0f"},
    "euro": {"suffix": "", "prefix": "€", "decimals": 0, "tick": ",.0f"},
    "percent": {"suffix": "%", "prefix": "", "decimals": 1, "tick": ",.1f"},
    "index": {"suffix": "", "prefix": "", "decimals": 1, "tick": ",.1f"},
    "rate": {"suffix": "", "prefix": "", "decimals": 2, "tick": ",.2f"},
    "m2": {"suffix": " m²", "prefix": "", "decimals": 0, "tick": ",.0f"},
}


def format_value(value: float | int | None, value_format: str = "number") -> str:
    """Render a single number the way a normal person expects to read it."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    spec = VALUE_FORMATS.get(value_format, VALUE_FORMATS["number"])
    decimals = spec["decimals"]
    body = f"{value:,.{decimals}f}"
    return f"{spec['prefix']}{body}{spec['suffix']}"


def format_delta(value: float | int | None, value_format: str = "number") -> str | None:
    """Render a change vs. the previous period, with a leading sign."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    spec = VALUE_FORMATS.get(value_format, VALUE_FORMATS["number"])
    decimals = spec["decimals"]
    # Use an ASCII hyphen-minus for negatives: st.metric decides the delta
    # arrow/colour by testing whether the string starts with "-", and a
    # typographic minus sign ("−", U+2212) is not recognised — it would make
    # a negative change render as a green upward arrow.
    sign = "+" if value >= 0 else "-"
    body = f"{abs(value):,.{decimals}f}"
    return f"{sign}{spec['prefix']}{body}{spec['suffix']}"


def axis_tickformat(value_format: str) -> str:
    return VALUE_FORMATS.get(value_format, VALUE_FORMATS["number"])["tick"]


def axis_tickprefix(value_format: str) -> str:
    return VALUE_FORMATS.get(value_format, VALUE_FORMATS["number"])["prefix"]


def axis_ticksuffix(value_format: str) -> str:
    return VALUE_FORMATS.get(value_format, VALUE_FORMATS["number"])["suffix"]


# Plain-language replacements for technical STATEC / SDMX column names.
FRIENDLY_COLUMN_NAMES = {
    "TIME_PERIOD": "Period",
    "OBS_VALUE": "Value",
    "OBS_STATUS": "Data status",
    "FREQ": "Frequency",
    "SPECIFICATION": "Breakdown",
    "NACE_REV2": "Economic sector",
    "GENDER": "Sex",
    "SEX": "Sex",
    "GEO": "Place",
    "AGE": "Age group",
    "NATIONALITY": "Nationality",
    "UNIT_MEASURE": "Unit",
    "PRODUCT_BCS": "Type of building",
    "DECIMALS": "Decimals",
}


def friendly_column(name: str) -> str:
    """Turn a raw STATEC column code into something readable."""
    base = str(name)
    is_label = base.endswith("_LABEL")
    if is_label:
        base = base[: -len("_LABEL")]
    return FRIENDLY_COLUMN_NAMES.get(base, base.replace("_", " ").strip().capitalize())

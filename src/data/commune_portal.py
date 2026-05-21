"""Build commune profiles from available official datasets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.cache import get_dataset_meta, list_cached_datasets, load_dataset
from src.catalog import catalog_dataframe, is_placeholder_dataset_id
from src.data_access import get_dataset
from src.data.communes import commune_by_name, list_communes, normalize_commune_name
from src.transforms import normalize_columns

TOPIC_ORDER = ["Population", "Housing", "Salaries", "Labour Market", "Prices & Inflation", "Economy", "Education", "Mobility"]
COMMUNE_HINTS = ("commune", "municipality", "municipal", "locality", "localité", "gemeinde")
GEOGRAPHY_COLUMNS = (
    "COMMUNE_LABEL",
    "COMMUNE",
    "GEO_LABEL",
    "GEO",
    "GEOGRAPHY_LABEL",
    "GEOGRAPHY",
    "LOCALITY_LABEL",
    "LOCALITY",
)


@dataclass(frozen=True)
class CommuneDataset:
    dataset_id: str
    title: str
    topic: str
    description: str
    geography_column: str | None
    value_column: str
    time_column: str
    source_status: str
    notes: str = ""
    default_filters: dict[str, str] | None = None


def _friendly_title(row: dict[str, Any], meta: dict[str, Any] | None = None) -> str:
    return (
        row.get("friendly_title")
        or row.get("title")
        or (meta or {}).get("name_en")
        or (meta or {}).get("name_fr")
        or row.get("dataset_id")
        or "Official dataset"
    )


def _find_geo_column(df: pd.DataFrame, entry: dict[str, Any] | None = None) -> str | None:
    entry = entry or {}
    for col in (entry.get("commune_name_column"), entry.get("geography_column"), entry.get("commune_code_column")):
        if col and col in df.columns:
            return col
    for col in GEOGRAPHY_COLUMNS:
        if col in df.columns:
            return col
    for col in df.columns:
        folded = col.lower()
        if any(hint in folded for hint in COMMUNE_HINTS):
            return col
    return None


def _guess_topic(dataset_id: str, title: str) -> str:
    text = f"{dataset_id} {title}".lower()
    if any(term in text for term in ("population", "resident", "habit", "demo")):
        return "Population"
    if any(term in text for term in ("housing", "house", "rent", "dwelling", "logement", "loyer")):
        return "Housing"
    if any(term in text for term in ("employ", "unemployment", "job", "labour", "travail", "chomage")):
        return "Labour Market"
    if any(term in text for term in ("price", "inflation", "prix")):
        return "Prices & Inflation"
    return "Other"


def find_commune_datasets(catalog: pd.DataFrame | None = None) -> list[CommuneDataset]:
    """Return datasets that are declared or detected as commune-level.

    Placeholder catalog rows are returned as source details only. Cached datasets
    are inspected for commune/geography columns so the portal can light up as
    soon as a real commune-level dataset is downloaded.
    """
    rows: list[CommuneDataset] = []
    catalog = catalog if catalog is not None else catalog_dataframe()
    catalog_by_id = {str(row["dataset_id"]): row for row in catalog.to_dict("records")}

    for row in catalog.to_dict("records"):
        if row.get("commune_portal") or row.get("geographic_level") == "commune":
            rows.append(
                CommuneDataset(
                    dataset_id=str(row["dataset_id"]),
                    title=_friendly_title(row),
                    topic=str(row.get("theme") or "Other"),
                    description=str(row.get("description") or ""),
                    geography_column=row.get("geography_column") or row.get("commune_name_column"),
                    value_column=str(row.get("value_column") or "OBS_VALUE"),
                    time_column=str(row.get("time_column") or "TIME_PERIOD"),
                    source_status=str(row.get("status") or "unknown"),
                    notes=str(row.get("notes") or ""),
                    default_filters=dict(row.get("default_filters") or {}),
                )
            )

    cached = list_cached_datasets()
    if cached.empty:
        return rows

    known = {item.dataset_id for item in rows}
    for cached_row in cached.to_dict("records"):
        dataset_id = str(cached_row.get("dataset_id") or "")
        if not dataset_id or dataset_id in known:
            continue
        try:
            df = normalize_columns(load_dataset(dataset_id))
        except Exception:
            continue
        geo_col = _find_geo_column(df)
        if not geo_col:
            continue
        meta = get_dataset_meta(dataset_id) or {}
        title = str(meta.get("name_en") or meta.get("name_fr") or dataset_id)
        rows.append(
            CommuneDataset(
                dataset_id=dataset_id,
                title=title,
                topic=_guess_topic(dataset_id, title),
                description="Cached official dataset with a commune/geography column.",
                geography_column=geo_col,
                value_column="OBS_VALUE" if "OBS_VALUE" in df.columns else "",
                time_column="TIME_PERIOD" if "TIME_PERIOD" in df.columns else "",
                source_status="cached",
                notes="Detected from cached dataset columns. Confirm metadata before promoting to the curated catalog.",
                default_filters={},
            )
        )
    return rows


def _apply_default_filters(df: pd.DataFrame, dataset: CommuneDataset) -> pd.DataFrame:
    work = df.copy()
    for column, expected in (dataset.default_filters or {}).items():
        if column not in work.columns:
            continue
        work = work[work[column].astype(str) == str(expected)]
    return work


def _only_commune_rows(df: pd.DataFrame, geo_col: str) -> pd.DataFrame:
    if df.empty or geo_col not in df.columns:
        return df.iloc[0:0].copy()
    known = {name.casefold() for name in list_communes()}
    return df[df[geo_col].astype(str).str.casefold().isin(known)].copy()


def filter_dataset_for_commune(df: pd.DataFrame, commune: str, dataset: CommuneDataset | None = None) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    canonical = normalize_commune_name(commune)
    info = dataset.__dict__ if dataset else {}
    geo_col = _find_geo_column(df, info)
    if not canonical or not geo_col:
        return df.iloc[0:0].copy()
    target = canonical.lower()
    code = commune_by_name(canonical).code if commune_by_name(canonical) else None
    work = df.copy()
    values = work[geo_col].astype(str)
    mask = values.str.casefold().eq(target.casefold())
    if code:
        mask = mask | values.str.strip().eq(str(int(code))) | values.str.strip().eq(code)
    return work[mask].copy()


def get_latest_commune_value(df: pd.DataFrame, value_col: str = "OBS_VALUE", time_col: str = "TIME_PERIOD") -> dict[str, Any] | None:
    if df.empty or value_col not in df.columns:
        return None
    work = df.copy()
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work = work.dropna(subset=[value_col])
    if work.empty:
        return None
    if time_col in work.columns:
        latest_period = work[time_col].dropna().astype(str).sort_values().iloc[-1]
        work = work[work[time_col].astype(str) == latest_period]
    else:
        latest_period = None
    return {"value": float(work[value_col].mean()), "period": latest_period}


def calculate_commune_trend(df: pd.DataFrame, value_col: str = "OBS_VALUE", time_col: str = "TIME_PERIOD") -> dict[str, Any] | None:
    if df.empty or value_col not in df.columns or time_col not in df.columns:
        return None
    work = df[[time_col, value_col]].copy()
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work = work.dropna(subset=[value_col])
    if work.empty:
        return None
    series = work.groupby(time_col, as_index=False)[value_col].mean().sort_values(time_col)
    if len(series) < 2:
        return None
    latest = float(series[value_col].iloc[-1])
    previous = float(series[value_col].iloc[-2])
    delta = latest - previous
    pct = (delta / previous * 100) if previous else None
    return {
        "delta": delta,
        "pct_change": pct,
        "latest_period": str(series[time_col].iloc[-1]),
        "previous_period": str(series[time_col].iloc[-2]),
    }


def compare_commune_to_national_average(
    df: pd.DataFrame,
    commune: str,
    value_col: str = "OBS_VALUE",
    time_col: str = "TIME_PERIOD",
    dataset: CommuneDataset | None = None,
) -> dict[str, Any] | None:
    geo_col = _find_geo_column(df, dataset.__dict__ if dataset else None)
    if df.empty or value_col not in df.columns or not geo_col:
        return None
    work = _only_commune_rows(df, geo_col)
    if time_col in work.columns and not work[time_col].dropna().empty:
        latest = work[time_col].dropna().astype(str).sort_values().iloc[-1]
        work = work[work[time_col].astype(str) == latest]
    else:
        latest = None
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    avg = work[value_col].dropna().mean()
    commune_df = filter_dataset_for_commune(work, commune)
    latest_value = get_latest_commune_value(commune_df, value_col=value_col, time_col=time_col)
    if latest_value is None or pd.isna(avg):
        return None
    return {"period": latest, "commune_value": latest_value["value"], "average": float(avg), "difference": latest_value["value"] - float(avg)}


def rank_commune_against_others(
    df: pd.DataFrame,
    commune: str,
    value_col: str = "OBS_VALUE",
    time_col: str = "TIME_PERIOD",
    dataset: CommuneDataset | None = None,
) -> dict[str, Any] | None:
    geo_col = _find_geo_column(df, dataset.__dict__ if dataset else None)
    if df.empty or not geo_col or value_col not in df.columns:
        return None
    work = _only_commune_rows(df, geo_col)
    if time_col in work.columns and not work[time_col].dropna().empty:
        latest = work[time_col].dropna().astype(str).sort_values().iloc[-1]
        work = work[work[time_col].astype(str) == latest]
    else:
        latest = None
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    ranking = work.dropna(subset=[value_col]).groupby(geo_col, as_index=False)[value_col].mean()
    if ranking.empty:
        return None
    ranking = ranking.sort_values(value_col, ascending=False).reset_index(drop=True)
    canonical = normalize_commune_name(commune)
    if not canonical:
        return None
    matches = ranking[ranking[geo_col].astype(str).str.casefold() == canonical.casefold()]
    if matches.empty:
        return None
    rank = int(matches.index[0] + 1)
    return {"rank": rank, "total": int(len(ranking)), "period": latest, "ranking": ranking}


def _load_commune_dataset(dataset: CommuneDataset, commune: str) -> dict[str, Any]:
    if is_placeholder_dataset_id(dataset.dataset_id):
        return {
            "dataset": dataset,
            "status": "placeholder",
            "rows": pd.DataFrame(),
            "latest": None,
            "trend": None,
            "comparison": None,
            "rank": None,
        }
    try:
        raw = normalize_columns(get_dataset(dataset.dataset_id))
    except Exception as exc:  # noqa: BLE001 - keep profile generation resilient
        return {"dataset": dataset, "status": "unavailable", "error": str(exc), "rows": pd.DataFrame()}
    raw = _apply_default_filters(raw, dataset)
    rows = filter_dataset_for_commune(raw, commune, dataset)
    latest = get_latest_commune_value(rows, dataset.value_column, dataset.time_column)
    return {
        "dataset": dataset,
        "status": "ready" if not rows.empty else "empty",
        "rows": rows,
        "latest": latest,
        "trend": calculate_commune_trend(rows, dataset.value_column, dataset.time_column),
        "comparison": compare_commune_to_national_average(raw, commune, dataset.value_column, dataset.time_column, dataset),
        "rank": rank_commune_against_others(raw, commune, dataset.value_column, dataset.time_column, dataset),
    }


def get_commune_profile(commune_name: str) -> dict[str, Any]:
    canonical = normalize_commune_name(commune_name) or commune_name
    commune = commune_by_name(canonical)
    datasets = find_commune_datasets()
    loaded = [_load_commune_dataset(dataset, canonical) for dataset in datasets]
    ready = [item for item in loaded if item.get("status") == "ready"]

    sections = {topic: [item for item in ready if item["dataset"].topic == topic] for topic in TOPIC_ORDER}
    other = [item for item in ready if item["dataset"].topic not in TOPIC_ORDER]
    if other:
        sections["Other"] = other

    overview_metrics = []
    for topic in TOPIC_ORDER:
        item = next((entry for entry in sections.get(topic, []) if entry.get("latest")), None)
        if item:
            latest = item["latest"]
            overview_metrics.append(
                {
                    "label": topic,
                    "value": latest["value"],
                    "period": latest.get("period"),
                    "dataset": item["dataset"].title,
                    "trend": item.get("trend"),
                }
            )
    overview_metrics.append(
        {
            "label": "Available local datasets",
            "value": float(len(ready)),
            "period": None,
            "dataset": "Cached official commune-level datasets",
            "trend": None,
        }
    )

    available_rows = []
    for item in loaded:
        dataset = item["dataset"]
        latest = item.get("latest") or {}
        available_rows.append(
            {
                "Topic": dataset.topic,
                "Dataset": dataset.title,
                "Dataset ID": dataset.dataset_id,
                "Latest value": latest.get("value"),
                "Time period": latest.get("period"),
                "Status": item.get("status"),
            }
        )

    return {
        "commune": canonical,
        "commune_code": commune.code if commune else None,
        "canton": commune.canton if commune else None,
        "overview_metrics": overview_metrics,
        "sections": sections,
        "available_datasets": available_rows,
        "loaded_datasets": loaded,
        "ready_count": len(ready),
        "placeholder_count": len([item for item in loaded if item.get("status") == "placeholder"]),
    }

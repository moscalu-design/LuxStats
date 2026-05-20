"""High-level dataset access functions used by pages."""

from __future__ import annotations

import pandas as pd

from src.cache import fetch_and_cache_dataset, is_dataset_cached, load_dataset, load_dataflows
from src.statec_client import Dataflow, StatecClient
from src.transforms import normalize_columns


def get_dataset(dataset_id: str, refresh: bool = False) -> pd.DataFrame:
    client = StatecClient()
    flows = load_dataflows(client)
    flow = next((item for item in flows if item.id == dataset_id), None)
    if flow is None:
        if is_dataset_cached(dataset_id) and not refresh:
            return normalize_columns(load_dataset(dataset_id))
        raise ValueError(f"Dataset {dataset_id} was not found in the LUSTAT dataflow list.")
    if refresh or not is_dataset_cached(dataset_id):
        df, _ = fetch_and_cache_dataset(client, flow, force_refresh=refresh)
        return normalize_columns(df)
    return normalize_columns(load_dataset(dataset_id))


def find_dataflows(query: str, limit: int = 25) -> list[Dataflow]:
    client = StatecClient()
    terms = [term for term in query.split() if term]
    flows = load_dataflows(client)
    if terms:
        flows = [flow for flow in flows if flow.matches(terms)]
    return sorted(flows, key=lambda flow: flow.id)[:limit]

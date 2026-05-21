from __future__ import annotations

from src.data.statec_api_catalog import (
    categorize_api_dataset,
    load_api_catalog,
    parse_lustat_dataflows,
)
from src.statec_client import Dataflow


def _flow(flow_id: str, name_en: str) -> Dataflow:
    return Dataflow(id=flow_id, agency="LU1", version="1.0",
                    name_en=name_en, name_fr="", structure_ref=None)


def test_parse_lustat_dataflows_shape() -> None:
    parsed = parse_lustat_dataflows([
        _flow("DF_X021", "Population by canton and municipality"),
        _flow("DF_C1202", "Average gross salary by sector"),
    ])
    assert len(parsed) == 2
    assert parsed[0]["dataset_id"] == "DF_X021"
    assert "title" in parsed[0] and "version" in parsed[0]


def test_categorize_api_dataset_uses_title() -> None:
    assert categorize_api_dataset("Population by municipality", "", "DF_X021") in {
        "Population", "Communes / Geography",
    }
    assert categorize_api_dataset("Average gross salary", "", "DF_C1202") == \
        "Salaries / Income"


def test_load_api_catalog_returns_a_list() -> None:
    catalog = load_api_catalog()
    assert isinstance(catalog, list)
    # When the catalog is built, every record carries the core fields.
    for record in catalog[:20]:
        assert record["source_type"] == "LUSTAT_API"
        assert record["dataset_id"]
        assert record["category"]

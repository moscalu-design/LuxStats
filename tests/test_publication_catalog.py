from __future__ import annotations

from src.data.statec_publication_catalog import (
    PUBLICATION_SERIES,
    _infer_date,
    load_publication_catalog,
)
from src.data.statec_web import is_allowed_url


def test_publication_series_are_well_formed() -> None:
    assert PUBLICATION_SERIES
    for slug, (family, _category) in PUBLICATION_SERIES.items():
        assert slug and family


def test_infer_date_from_url() -> None:
    assert _infer_date("/catalogue-publications/logement/2025/logement-02-25.pdf") == "2025"
    assert _infer_date("/no/year/here.pdf") is None


def test_publication_records_stay_on_official_domains() -> None:
    for record in load_publication_catalog():
        assert is_allowed_url(record["file_url"]), record["file_url"]
        assert record["source_type"] in {"PUBLICATION_PDF", "PUBLICATION_EXCEL"}


def test_load_publication_catalog_returns_a_list() -> None:
    assert isinstance(load_publication_catalog(), list)

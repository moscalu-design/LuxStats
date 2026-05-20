"""Thin client for the LUSTAT (STATEC Luxembourg) SDMX REST API.

Docs: https://lustat.statec.lu/ — the service exposes a .Stat Suite SDMX REST
endpoint at https://lustat.statec.lu/rest/.
"""

from __future__ import annotations

import io
import time
from dataclasses import dataclass
from typing import Any, Iterable
from xml.etree import ElementTree as ET

import pandas as pd
import requests

BASE_URL = "https://lustat.statec.lu/rest"
AGENCY = "LU1"

# SDMX-CSV 1.0 with both codes and labels — useful for downstream LLM/analytics
SDMX_CSV_ACCEPT = "application/vnd.sdmx.data+csv;version=1.0.0;labels=both"
SDMX_XML_ACCEPT = "application/vnd.sdmx.structure+xml;version=2.1"

NS = {
    "mes": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "str": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "com": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}


@dataclass(frozen=True)
class Dataflow:
    id: str
    agency: str
    version: str
    name_en: str
    name_fr: str
    structure_ref: str | None = None

    @property
    def flow_ref(self) -> str:
        return f"{self.agency},{self.id},{self.version}"

    @property
    def display(self) -> str:
        label = self.name_en or self.name_fr or self.id
        return f"{self.id} — {label}"

    def matches(self, terms: Iterable[str]) -> bool:
        haystack = " ".join(
            [self.id, self.name_en or "", self.name_fr or ""]
        ).lower()
        return all(t.lower() in haystack for t in terms if t)


class StatecClient:
    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: int = 60,
        retries: int = 3,
        backoff: float = 1.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.session = requests.Session()

    def _get(self, path: str, accept: str, params: dict | None = None) -> requests.Response:
        url = f"{self.base_url}{path}"
        last_exc: Exception | None = None
        for attempt in range(self.retries):
            try:
                resp = self.session.get(
                    url,
                    headers={"Accept": accept},
                    params=params,
                    timeout=self.timeout,
                )
                if resp.status_code == 429 or resp.status_code >= 500:
                    raise requests.HTTPError(f"{resp.status_code} from {url}")
                resp.raise_for_status()
                return resp
            except requests.RequestException as exc:
                last_exc = exc
                if attempt == self.retries - 1:
                    break
                time.sleep(self.backoff ** attempt)
        raise RuntimeError(f"Failed to GET {url}: {last_exc}")

    def list_dataflows(self) -> list[Dataflow]:
        resp = self._get(f"/dataflow/{AGENCY}/all/all", accept=SDMX_XML_ACCEPT)
        return _parse_dataflows(resp.content)

    def get_data_csv(
        self,
        flow_ref: str,
        key: str = "all",
        params: dict | None = None,
    ) -> str:
        """Fetch a dataflow's data as SDMX-CSV. `flow_ref` is `AGENCY,ID,VERSION`."""
        resp = self._get(
            f"/data/{flow_ref}/{key}",
            accept=SDMX_CSV_ACCEPT,
            params=params,
        )
        return resp.text

    def get_data_df(
        self,
        flow_ref: str,
        key: str = "all",
        params: dict | None = None,
    ) -> pd.DataFrame:
        csv_text = self.get_data_csv(flow_ref, key=key, params=params)
        return parse_sdmx_csv(csv_text)


def parse_sdmx_csv(csv_text: str) -> pd.DataFrame:
    """Parse SDMX-CSV with labels=both into a tidy DataFrame.

    SDMX-CSV with labels=both produces columns like ``GEO: Geographic area``
    whose cell values look like ``LU: Luxembourg``. We split each column into
    a code column and label column, keeping the dataset's original meaning.
    """
    if not csv_text.strip():
        return pd.DataFrame()
    raw = pd.read_csv(io.StringIO(csv_text), dtype=str, keep_default_na=False)
    out = pd.DataFrame(index=raw.index)
    for col in raw.columns:
        # split "DIM_ID: Dimension name" header
        if ":" in col:
            code_name, label_name = [p.strip() for p in col.split(":", 1)]
        else:
            code_name, label_name = col.strip(), col.strip()
        values = raw[col].fillna("")
        if values.str.contains(":", regex=False).any():
            split = values.str.split(":", n=1, expand=True)
            codes = split[0].str.strip()
            labels = split[1].fillna("").str.strip()
            out[code_name] = codes
            if label_name and label_name != code_name:
                out[f"{code_name}_LABEL"] = labels
        else:
            out[code_name] = values
    # OBS_VALUE → numeric where possible
    if "OBS_VALUE" in out.columns:
        out["OBS_VALUE"] = pd.to_numeric(out["OBS_VALUE"], errors="coerce")
    if "TIME_PERIOD" in out.columns:
        out["TIME_PERIOD"] = out["TIME_PERIOD"].astype(str)
    return out


def _parse_dataflows(xml_bytes: bytes) -> list[Dataflow]:
    root = ET.fromstring(xml_bytes)
    flows: list[Dataflow] = []
    for df in root.iter(f"{{{NS['str']}}}Dataflow"):
        df_id = df.attrib.get("id", "")
        agency = df.attrib.get("agencyID", AGENCY)
        version = df.attrib.get("version", "1.0")
        names = {
            n.attrib.get(f"{{http://www.w3.org/XML/1998/namespace}}lang", ""): (n.text or "")
            for n in df.findall(f"{{{NS['com']}}}Name")
        }
        struct_ref = None
        ref = df.find(f"{{{NS['str']}}}Structure/{{{NS['mes']}}}Ref") or df.find(
            f"{{{NS['str']}}}Structure/Ref"
        )
        if ref is not None:
            struct_ref = ref.attrib.get("id")
        flows.append(
            Dataflow(
                id=df_id,
                agency=agency,
                version=version,
                name_en=names.get("en", ""),
                name_fr=names.get("fr", ""),
                structure_ref=struct_ref,
            )
        )
    return flows


SALARY_KEYWORDS = [
    "salary", "salaire", "wage", "wages", "earnings", "income",
    "revenu", "rémunération", "remuneration",
    "occupation", "profession",
    "commune", "municipality",
    "sector", "secteur", "naceec", "nace",
    "gender", "sexe", "sex",
    "education", "éducation", "diploma", "diplôme",
    "decile", "déciles", "quantile", "percentile",
]


def filter_salary_related(flows: list[Dataflow]) -> list[Dataflow]:
    return [f for f in flows if any(f.matches([kw]) for kw in SALARY_KEYWORDS)]

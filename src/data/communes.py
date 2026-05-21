"""Luxembourg commune names, aliases, and cautious matching helpers."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from difflib import get_close_matches


@dataclass(frozen=True)
class Commune:
    name: str
    code: str
    canton: str


# Current 100 communes from Luxembourg geoportal collection 302, checked in May 2026.
COMMUNES: tuple[Commune, ...] = (
    Commune("Beaufort", "0042", "Echternach"),
    Commune("Bech", "0041", "Echternach"),
    Commune("Beckerich", "0011", "Redange"),
    Commune("Berdorf", "0090", "Echternach"),
    Commune("Bertrange", "0085", "Luxembourg"),
    Commune("Bettembourg", "0037", "Esch-sur-Alzette"),
    Commune("Bettendorf", "0096", "Diekirch"),
    Commune("Betzdorf", "0062", "Grevenmacher"),
    Commune("Bissen", "0043", "Mersch"),
    Commune("Biwer", "0076", "Grevenmacher"),
    Commune("Boulaide", "0070", "Wiltz"),
    Commune("Bourscheid", "0058", "Diekirch"),
    Commune("Bous-Waldbredimus", "0073", "Remich"),
    Commune("Clervaux", "0064", "Clervaux"),
    Commune("Colmar-Berg", "0045", "Mersch"),
    Commune("Consdorf", "0020", "Echternach"),
    Commune("Contern", "0024", "Luxembourg"),
    Commune("Dalheim", "0055", "Remich"),
    Commune("Diekirch", "0057", "Diekirch"),
    Commune("Differdange", "0023", "Esch-sur-Alzette"),
    Commune("Dippach", "0094", "Capellen"),
    Commune("Dudelange", "0060", "Esch-sur-Alzette"),
    Commune("Echternach", "0074", "Echternach"),
    Commune("Ell", "0071", "Redange"),
    Commune("Erpeldange-sur-Sûre", "0046", "Diekirch"),
    Commune("Esch-sur-Alzette", "0083", "Esch-sur-Alzette"),
    Commune("Esch-sur-Sûre", "0008", "Wiltz"),
    Commune("Ettelbruck", "0019", "Diekirch"),
    Commune("Feulen", "0025", "Diekirch"),
    Commune("Fischbach", "0100", "Mersch"),
    Commune("Flaxweiler", "0026", "Grevenmacher"),
    Commune("Frisange", "0006", "Esch-sur-Alzette"),
    Commune("Garnich", "0050", "Capellen"),
    Commune("Goesdorf", "0039", "Wiltz"),
    Commune("Grevenmacher", "0063", "Grevenmacher"),
    Commune("Groussbus-Wal", "0053", "Redange"),
    Commune("Habscht", "0059", "Capellen"),
    Commune("Heffingen", "0056", "Mersch"),
    Commune("Helperknapp", "0051", "Mersch"),
    Commune("Hesperange", "0002", "Luxembourg"),
    Commune("Junglinster", "0069", "Grevenmacher"),
    Commune("Kayl", "0022", "Esch-sur-Alzette"),
    Commune("Kehlen", "0017", "Capellen"),
    Commune("Kiischpelt", "0010", "Wiltz"),
    Commune("Koerich", "0040", "Capellen"),
    Commune("Kopstal", "0081", "Capellen"),
    Commune("Käerjeng", "0048", "Capellen"),
    Commune("Lac de la Haute-Sûre", "0066", "Wiltz"),
    Commune("Larochette", "0036", "Mersch"),
    Commune("Lenningen", "0016", "Remich"),
    Commune("Leudelange", "0072", "Esch-sur-Alzette"),
    Commune("Lintgen", "0004", "Mersch"),
    Commune("Lorentzweiler", "0027", "Mersch"),
    Commune("Luxembourg", "0098", "Luxembourg"),
    Commune("Mamer", "0030", "Capellen"),
    Commune("Manternach", "0061", "Grevenmacher"),
    Commune("Mersch", "0044", "Mersch"),
    Commune("Mertert", "0001", "Grevenmacher"),
    Commune("Mertzig", "0067", "Diekirch"),
    Commune("Mondercange", "0012", "Esch-sur-Alzette"),
    Commune("Mondorf-les-Bains", "0087", "Remich"),
    Commune("Niederanven", "0097", "Luxembourg"),
    Commune("Nommern", "0028", "Mersch"),
    Commune("Parc Hosingen", "0091", "Clervaux"),
    Commune("Préizerdaul", "0031", "Redange"),
    Commune("Putscheid", "0075", "Vianden"),
    Commune("Pétange", "0049", "Esch-sur-Alzette"),
    Commune("Rambrouch", "0092", "Redange"),
    Commune("Reckange-sur-Mess", "0052", "Esch-sur-Alzette"),
    Commune("Redange/Attert", "0047", "Redange"),
    Commune("Reisdorf", "0021", "Diekirch"),
    Commune("Remich", "0099", "Remich"),
    Commune("Roeser", "0086", "Esch-sur-Alzette"),
    Commune("Rosport-Mompach", "0082", "Echternach"),
    Commune("Rumelange", "0084", "Esch-sur-Alzette"),
    Commune("Saeul", "0014", "Redange"),
    Commune("Sandweiler", "0089", "Luxembourg"),
    Commune("Sanem", "0005", "Esch-sur-Alzette"),
    Commune("Schengen", "0093", "Remich"),
    Commune("Schieren", "0015", "Diekirch"),
    Commune("Schifflange", "0065", "Esch-sur-Alzette"),
    Commune("Schuttrange", "0009", "Luxembourg"),
    Commune("Stadtbredimus", "0033", "Remich"),
    Commune("Steinfort", "0029", "Capellen"),
    Commune("Steinsel", "0035", "Luxembourg"),
    Commune("Strassen", "0080", "Luxembourg"),
    Commune("Tandel", "0003", "Vianden"),
    Commune("Troisvierges", "0013", "Clervaux"),
    Commune("Useldange", "0079", "Redange"),
    Commune("Vallée de l'Ernz", "0054", "Diekirch"),
    Commune("Vianden", "0068", "Vianden"),
    Commune("Vichten", "0034", "Redange"),
    Commune("Waldbillig", "0077", "Echternach"),
    Commune("Walferdange", "0007", "Luxembourg"),
    Commune("Weiler-la-Tour", "0038", "Luxembourg"),
    Commune("Weiswampach", "0032", "Clervaux"),
    Commune("Wiltz", "0078", "Wiltz"),
    Commune("Wincrange", "0018", "Clervaux"),
    Commune("Winseler", "0088", "Wiltz"),
    Commune("Wormeldange", "0095", "Grevenmacher"),
)

ALIASES = {
    "luxembourg city": "Luxembourg",
    "luxembourg ville": "Luxembourg",
    "luxembourg-ville": "Luxembourg",
    "ville de luxembourg": "Luxembourg",
    "esch alzette": "Esch-sur-Alzette",
    "esch sur alzette": "Esch-sur-Alzette",
    "esch": "Esch-sur-Alzette",
    "dudelange": "Dudelange",
    "differdange": "Differdange",
    "hesperange": "Hesperange",
    "petange": "Pétange",
    "kaerjeng": "Käerjeng",
    "preizerdaul": "Préizerdaul",
    "erpeldange sure": "Erpeldange-sur-Sûre",
    "esch sure": "Esch-sur-Sûre",
    "lac haute sure": "Lac de la Haute-Sûre",
    "vallee de l ernz": "Vallée de l'Ernz",
}


def _fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


_BY_NORMALIZED = {_fold(commune.name): commune for commune in COMMUNES}
_ALIAS_TO_NAME = {_fold(alias): name for alias, name in ALIASES.items()}


def list_communes() -> list[str]:
    return [commune.name for commune in COMMUNES]


def commune_by_name(name: str) -> Commune | None:
    canonical = normalize_commune_name(name)
    return next((commune for commune in COMMUNES if commune.name == canonical), None)


def normalize_commune_name(name: str) -> str | None:
    key = _fold(name)
    if not key:
        return None
    if key in _ALIAS_TO_NAME:
        return _ALIAS_TO_NAME[key]
    commune = _BY_NORMALIZED.get(key)
    return commune.name if commune else None


def commune_suggestions(query: str, limit: int = 6) -> list[str]:
    key = _fold(query)
    if not key:
        return list_communes()[:limit]
    direct = normalize_commune_name(query)
    if direct:
        return [direct]
    scored = [name for folded, commune in _BY_NORMALIZED.items() if key in folded for name in [commune.name]]
    if scored:
        return scored[:limit]
    matches = get_close_matches(key, list(_BY_NORMALIZED), n=limit, cutoff=0.82)
    return [_BY_NORMALIZED[match].name for match in matches]


def extract_commune_from_query(query: str) -> str | None:
    key = _fold(query)
    if not key:
        return None
    for alias, canonical in _ALIAS_TO_NAME.items():
        if re.search(rf"\b{re.escape(alias)}\b", key):
            return canonical
    for folded, commune in sorted(_BY_NORMALIZED.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf"\b{re.escape(folded)}\b", key):
            return commune.name
    return None


def commune_search_terms() -> set[str]:
    terms = set(_BY_NORMALIZED)
    terms.update(_ALIAS_TO_NAME)
    return terms

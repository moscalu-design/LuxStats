"""Transparent, rule-based categorization for STATEC sources.

No machine learning and no language model — categorization is a set of
plain keyword rules, easy to read and edit. Rules match against the combined
title, description, id, filename and URL of a source, in English and French
(STATEC publishes bilingually).
"""

from __future__ import annotations

import re
import unicodedata

# The fixed set of portal categories. "Other / Unknown" is the fallback.
CATEGORIES: list[str] = [
    "Population",
    "Communes / Geography",
    "Housing",
    "Salaries / Income",
    "Labour Market",
    "Prices / Inflation",
    "Economy / National Accounts",
    "Public Finance",
    "Enterprises / Business",
    "Construction",
    "Tourism",
    "Transport",
    "Education",
    "Health",
    "Social Conditions",
    "Environment / Energy",
    "Agriculture",
    "Crime / Justice",
    "Elections",
    "Other / Unknown",
]

# Category -> keywords (English + French). Order is the tie-break priority:
# earlier categories win when keyword-match counts are equal.
CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Housing", [
        "housing", "dwelling", "dwellings", "rent", "rents", "rental",
        "logement", "logements", "loyer", "loyers", "real estate",
        "property price", "acquisition price", "house price", "prix des logements",
        "immobilier", "habitation", "appartement", "apartment",
    ]),
    ("Salaries / Income", [
        "salary", "salaries", "wage", "wages", "earnings", "income",
        "salaire", "salaires", "remuneration", "rémunération", "revenu",
        "revenus", "minimum wage", "salaire minimum", "pay", "purchasing power",
    ]),
    ("Prices / Inflation", [
        "cpi", "ncpi", "hcpi", "hicp", "inflation", "consumer price",
        "price index", "prix a la consommation", "prix à la consommation",
        "indice des prix", "cost of living", "deflator",
    ]),
    ("Labour Market", [
        "employment", "unemployment", "labour", "labor", "jobs", "job market",
        "emploi", "chomage", "chômage", "travail", "workforce", "worker",
        "vacancies", "main-d'oeuvre", "marche du travail",
    ]),
    ("Population", [
        "population", "resident", "residents", "inhabitant", "demographic",
        "demography", "births", "deaths", "migration", "nationality",
        "nationalite", "age", "fertility", "mortality", "naissances", "deces",
        "natalite", "census", "recensement",
    ]),
    ("Communes / Geography", [
        "commune", "communes", "municipality", "municipalities", "canton",
        "cantons", "geographical", "geography", "lau", "locality", "localite",
        "territoire", "land use", "geographique", "by geographical",
    ]),
    ("Economy / National Accounts", [
        "gdp", "gross domestic product", "national accounts", "comptes nationaux",
        "value added", "economic outlook", "conjoncture", "balance of payments",
        "pib", "macroeconomic", "economie", "productivity",
    ]),
    ("Public Finance", [
        "public finance", "government", "budget", "tax", "taxes", "fiscal",
        "debt", "deficit", "finances publiques", "pension", "pensions",
        "social security", "recettes", "depenses publiques",
    ]),
    ("Enterprises / Business", [
        "enterprise", "enterprises", "business", "company", "companies",
        "entreprise", "entreprises", "turnover", "firm", "self-employed",
        "industrial production", "sector activity",
    ]),
    ("Construction", [
        "construction", "building permit", "building permits", "permis de batir",
        "permis de construire", "batiment", "buildings authorised", "civil engineering",
    ]),
    ("Tourism", [
        "tourism", "tourist", "tourisme", "nights", "arrivals", "hotel",
        "hotels", "overnight stays", "accommodation", "hebergement",
    ]),
    ("Transport", [
        "transport", "mobility", "traffic", "vehicle", "vehicles", "car",
        "cars", "mobilite", "trafic", "road", "rail", "commute", "commuting",
    ]),
    ("Education", [
        "education", "school", "schools", "pupil", "pupils", "student",
        "students", "university", "ecole", "enseignement", "eleves",
        "diploma", "diplome", "training", "formation",
    ]),
    ("Health", [
        "health", "hospital", "hospitals", "mortality", "disease", "sante",
        "hopital", "medical", "morbidity", "care", "life expectancy",
    ]),
    ("Environment / Energy", [
        "environment", "energy", "climate", "emissions", "waste", "water",
        "environnement", "energie", "climat", "dechets", "renewable",
        "greenhouse", "pollution", "electricity",
    ]),
    ("Agriculture", [
        "agriculture", "agricultural", "farm", "farms", "crop", "crops",
        "livestock", "viticulture", "wine", "vineyard", "forestry", "agricole",
    ]),
    ("Crime / Justice", [
        "crime", "criminality", "criminalite", "justice", "police", "court",
        "courts", "offence", "accidents", "delinquance", "prison",
    ]),
    ("Elections", [
        "election", "elections", "vote", "votes", "voting", "referendum",
        "electoral", "electorale",
    ]),
    ("Social Conditions", [
        "social", "poverty", "inequality", "living conditions", "well-being",
        "conditions sociales", "conditions de vie", "pauvrete", "exclusion",
        "household budget", "social protection", "deprivation",
    ]),
]


def _fold(text: str) -> str:
    """Lowercase and strip accents for robust bilingual matching."""
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def categorize(text: str) -> str:
    """Return the best-matching category for a piece of source text."""
    folded = _fold(text)
    if not folded.strip():
        return "Other / Unknown"
    best_category = "Other / Unknown"
    best_score = 0
    for category, keywords in CATEGORY_RULES:
        score = sum(1 for kw in keywords if _fold(kw) in folded)
        if score > best_score:
            best_score = score
            best_category = category
    return best_category


def category_scores(text: str) -> dict[str, int]:
    """Return the keyword-match score for every category (for diagnostics)."""
    folded = _fold(text)
    return {
        category: sum(1 for kw in keywords if _fold(kw) in folded)
        for category, keywords in CATEGORY_RULES
    }


# Geography inference -------------------------------------------------------

_COMMUNE_HINTS = ["commune", "municipalit", "gemeinde", "localite", "locality",
                  " lau", "par commune", "by municipality"]
_CANTON_HINTS = ["canton"]
_REGION_HINTS = ["region", "région", "regional"]
_NATIONAL_HINTS = ["national", "pays", "country", "luxembourg total",
                   "whole country", "ensemble du pays"]


def infer_geographic_level(text: str) -> str:
    """Infer national / commune / canton / region / unknown from source text."""
    folded = _fold(text)
    if any(hint in folded for hint in _COMMUNE_HINTS):
        return "commune"
    if any(hint in folded for hint in _CANTON_HINTS):
        return "canton"
    if any(hint in folded for hint in _REGION_HINTS):
        return "region"
    if any(hint in folded for hint in _NATIONAL_HINTS):
        return "national"
    return "unknown"


# Keyword extraction --------------------------------------------------------

_STOPWORDS = {
    "the", "and", "of", "in", "by", "for", "to", "a", "an", "on", "with",
    "de", "des", "du", "la", "le", "les", "et", "en", "par", "au", "aux",
    "selon", "pour", "data", "table", "tableau",
}


def extract_keywords(text: str, limit: int = 12) -> list[str]:
    """Extract simple, de-duplicated keywords from source text."""
    folded = _fold(text)
    tokens = re.findall(r"[a-z0-9]{3,}", folded)
    seen: list[str] = []
    for token in tokens:
        if token in _STOPWORDS or token.isdigit():
            continue
        if token not in seen:
            seen.append(token)
        if len(seen) >= limit:
            break
    return seen


def looks_like_commune_data(text: str) -> bool:
    return infer_geographic_level(text) in {"commune", "canton"}


def looks_like_housing_data(text: str) -> bool:
    return categorize(text) == "Housing"


def looks_like_short_term_indicator(text: str) -> bool:
    folded = _fold(text)
    return any(h in folded for h in [
        "short-term", "short term", "indicateur court", "court terme",
        "conjoncture", "monthly indicator", "current indicator",
    ])

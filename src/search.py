"""Universal search: map everyday words to curated statistics.

This powers the home-page search box. It is deliberately forgiving — it
understands synonyms ("pay", "wages", "income" all mean salary) so visitors
never need to know STATEC vocabulary.
"""

from __future__ import annotations

from src.concepts import Concept, all_concepts
from src.data.communes import extract_commune_from_query
from src.data.source_catalog import load_unified_source_catalog
from src.data.source_visualization import load_source_visualization_index

# Synonym groups. Any word in a group expands the query with the whole group,
# so "house" also searches "housing", "property", "real estate", etc.
SYNONYM_GROUPS: list[list[str]] = [
    ["salary", "salaries", "wage", "wages", "pay", "income", "earnings", "paid"],
    ["house", "housing", "home", "homes", "apartment", "flat", "property",
     "real estate", "dwelling", "construction"],
    ["rent", "rents", "rental", "renting"],
    ["people", "population", "residents", "inhabitants", "demographics"],
    ["job", "jobs", "work", "employment", "unemployment", "labour", "labor"],
    ["inflation", "prices", "price", "cpi", "cost of living", "expensive"],
    ["commune", "communes", "municipality", "town", "city", "canton"],
    ["tourism", "tourist", "tourists", "arrivals", "hotel", "hotels",
     "overnight stays", "nights", "accommodation", "d5301", "d5310"],
    ["ai", "artificial intelligence", "machine learning", "ml",
     "generative ai", "genai", "chatbot", "chatbots", "automation",
     "ai adoption", "ai use", "enterprise ai", "ai luxembourg"],
]


def _expand(terms: list[str]) -> set[str]:
    expanded: set[str] = set(terms)
    joined = " ".join(terms)
    for group in SYNONYM_GROUPS:
        if any(word in joined for word in group):
            expanded.update(group)
    return expanded


def search_concepts(query: str, limit: int = 8) -> list[Concept]:
    """Return the best-matching curated concepts for a free-text query."""
    query = (query or "").strip().lower()
    concepts = all_concepts()
    if not query:
        return [c for c in concepts if c.recommended][:limit]

    raw_terms = [t for t in query.replace(",", " ").split() if t]
    terms = _expand(raw_terms)

    scored: list[tuple[float, int, Concept]] = []
    for order, concept in enumerate(concepts):
        haystack = concept.search_text
        keyword_text = " ".join(concept.keywords).lower()
        score = 0.0
        for term in terms:
            if term in concept.title.lower():
                score += 5
            if term in keyword_text:
                score += 3
            elif term in haystack:
                score += 1
        # Whole-phrase match is a strong signal.
        if query in haystack:
            score += 6
        if score <= 0:
            continue
        if concept.recommended:
            score += 1
        if concept.popular:
            score += 0.5
        scored.append((score, order, concept))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [concept for _, _, concept in scored[:limit]]


def _commune_tab(query: str) -> str:
    query = query.casefold()
    if any(term in query for term in ("housing", "house", "rent", "property")):
        return "Housing"
    if any(term in query for term in ("population", "people", "resident")):
        return "Population"
    if any(term in query for term in ("salary", "salar", "wage", "pay")):
        return "Salaries"
    if any(term in query for term in ("labour", "labor", "job", "unemployment", "employment")):
        return "Labour"
    return "Overview"


def search_communes(query: str) -> list[dict[str, str]]:
    """Return Commune Portal search hits for recognized commune-name queries."""
    commune = extract_commune_from_query(query)
    if not commune:
        return []
    tab = _commune_tab(query)
    description = f"Open the local statistics profile for {commune}, starting from {tab.lower()}."
    return [
        {
            "commune": commune,
            "tab": tab,
            "title": f"{commune} commune profile",
            "description": description,
        }
    ]


def search_source_visualizations(query: str, limit: int = 10) -> list[dict]:
    """Return source-index matches ranked by safe visualization usefulness."""
    query = (query or "").strip().casefold()
    if not query:
        return []
    terms = _expand([t for t in query.replace(",", " ").split() if t])
    status_weight = {
        "chart_ready": 100,
        "preview_ready": 70,
        "needs_column_mapping": 45,
        "needs_excel_inspection": 40,
        "downloadable_only": 30,
        "needs_manual_review": 20,
        "not_chartable": 5,
        "ignored_low_priority": 0,
    }
    catalog_by_id = {row.get("source_id"): row for row in load_unified_source_catalog()}
    scored: list[tuple[int, str, dict]] = []
    for row in load_source_visualization_index():
        source_record = catalog_by_id.get(row.get("source_id"), {})
        haystack = " ".join(
            str(row.get(field, ""))
            for field in ("title", "category", "source_type", "dataset_id", "source_id", "reason")
        ).casefold()
        haystack = f"{haystack} {' '.join(source_record.get('keywords', []) or [])}".casefold()
        score = 0
        for term in terms:
            if term in haystack:
                score += 5
            if term in str(row.get("title", "")).casefold():
                score += 5
            if term in str(row.get("category", "")).casefold():
                score += 2
        if query in haystack:
            score += 8
        if score <= 0:
            continue
        score += status_weight.get(str(row.get("visualization_status")), 0)
        score += int(row.get("priority_score") or 0)
        scored.append((score, str(row.get("title", "")), row))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [row for _, _, row in scored[:limit]]


NO_RESULTS_HINT = (
    "No exact match found. Try searching for **salary**, **housing**, "
    "**population**, **inflation**, **unemployment**, **tourism**, or a commune such as **Hesperange**."
)

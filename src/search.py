"""Universal search: map everyday words to curated statistics.

This powers the home-page search box. It is deliberately forgiving — it
understands synonyms ("pay", "wages", "income" all mean salary) so visitors
never need to know STATEC vocabulary.
"""

from __future__ import annotations

from src.concepts import Concept, all_concepts

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


NO_RESULTS_HINT = (
    "No exact match found. Try searching for **salary**, **housing**, "
    "**population**, **inflation**, or **unemployment**."
)

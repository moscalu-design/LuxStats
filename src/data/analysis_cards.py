"""Guided analysis cards: ready-made user journeys, not raw datasets.

Each card answers a human question ("Which communes are growing fastest?")
and routes either to a curated concept chart or to a product page. Cards are
curated by hand so the home page can lead with high-value journeys.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.concepts import get_concept


@dataclass(frozen=True)
class AnalysisCard:
    """One pre-built analysis journey."""

    id: str
    title: str                       # human question / journey title
    blurb: str                       # one-sentence plain-English explanation
    topic: str                       # portal topic tag
    difficulty: str                  # "beginner" or "intermediate"
    icon: str                        # emoji icon
    section: str                     # "popular" / "comparison" / "commune" / "changes"
    concept_id: str | None = None    # opens this curated concept chart inline
    page: str | None = None          # or routes to this page path


# --------------------------------------------------------------------------
# Curated cards. concept_id values must exist in src/concepts.py; page values
# must point at a real page file. Both are validated in tests.
# --------------------------------------------------------------------------

ANALYSIS_CARDS: list[AnalysisCard] = [
    # ---- Popular statistics (open a concept chart) -----------------------
    AnalysisCard(
        id="where_salaries_highest",
        title="Where are salaries highest?",
        blurb="See which parts of the economy pay the most, ranked by average salary.",
        topic="Salaries",
        difficulty="beginner",
        icon="💶",
        section="popular",
        concept_id="salary_by_sector",
    ),
    AnalysisCard(
        id="population_over_time",
        title="How has the population changed?",
        blurb="Track how many people live in Luxembourg, year by year.",
        topic="Population",
        difficulty="beginner",
        icon="👥",
        section="popular",
        concept_id="population_growth",
    ),
    AnalysisCard(
        id="track_inflation",
        title="How fast are prices rising?",
        blurb="Follow Luxembourg's yearly inflation rate — the cost-of-living change.",
        topic="Prices & Inflation",
        difficulty="beginner",
        icon="📈",
        section="popular",
        concept_id="inflation_rate",
    ),
    AnalysisCard(
        id="housing_supply",
        title="How much new housing is built?",
        blurb="See how many new homes get building permits each year.",
        topic="Housing",
        difficulty="beginner",
        icon="🏠",
        section="popular",
        concept_id="new_homes",
    ),
    AnalysisCard(
        id="jobs_health",
        title="How healthy is the job market?",
        blurb="Compare the number of people in work with the number out of work.",
        topic="Labour Market",
        difficulty="beginner",
        icon="🧰",
        section="popular",
        concept_id="jobs_unemployment",
    ),
    AnalysisCard(
        id="gender_pay_gap",
        title="Is there a gender pay gap?",
        blurb="Compare average pay for women and men across the economy.",
        topic="Salaries",
        difficulty="intermediate",
        icon="⚖️",
        section="popular",
        concept_id="gender_pay",
    ),
    # ---- Common comparisons (route to the Compare page) ------------------
    AnalysisCard(
        id="compare_salary_sectors",
        title="Compare salary by sector",
        blurb="Put several industries side by side and see how their pay differs.",
        topic="Salaries",
        difficulty="beginner",
        icon="📊",
        section="comparison",
        page="pages/4_Compare.py",
    ),
    AnalysisCard(
        id="compare_communes_population",
        title="Compare communes head to head",
        blurb="Luxembourg City vs Hesperange vs Esch — population and more, side by side.",
        topic="Population",
        difficulty="beginner",
        icon="📍",
        section="comparison",
        page="pages/4_Compare.py",
    ),
    AnalysisCard(
        id="compare_inflation_categories",
        title="Compare trends over time",
        blurb="Track two or more statistics together to spot how they move.",
        topic="Prices & Inflation",
        difficulty="intermediate",
        icon="📉",
        section="comparison",
        page="pages/4_Compare.py",
    ),
    # ---- Explore by commune ---------------------------------------------
    AnalysisCard(
        id="explore_one_commune",
        title="Explore one commune",
        blurb="Pick a commune and see all of its local statistics in one place.",
        topic="Communes",
        difficulty="beginner",
        icon="🗺️",
        section="commune",
        page="pages/3_Commune_Portal.py",
    ),
    AnalysisCard(
        id="fastest_growing_communes",
        title="Which communes are growing fastest?",
        blurb="Rank communes by how much their population changed recently.",
        topic="Population",
        difficulty="intermediate",
        icon="🚀",
        section="commune",
        page="pages/5_What_Changed.py",
    ),
    # ---- What changed ----------------------------------------------------
    AnalysisCard(
        id="what_changed_recently",
        title="What changed recently?",
        blurb="See the latest available figures and the biggest recent moves.",
        topic="Updates",
        difficulty="beginner",
        icon="🆕",
        section="changes",
        page="pages/5_What_Changed.py",
    ),
    AnalysisCard(
        id="build_your_own",
        title="Build your own chart",
        blurb="Pick a topic, a metric and a chart type — no dataset codes needed.",
        topic="Tools",
        difficulty="beginner",
        icon="🛠️",
        section="changes",
        page="pages/2_Build_a_Chart.py",
    ),
]

CARDS_BY_ID: dict[str, AnalysisCard] = {card.id: card for card in ANALYSIS_CARDS}


def all_cards() -> list[AnalysisCard]:
    return list(ANALYSIS_CARDS)


def get_card(card_id: str) -> AnalysisCard | None:
    return CARDS_BY_ID.get(card_id)


def cards_in_section(section: str) -> list[AnalysisCard]:
    return [card for card in ANALYSIS_CARDS if card.section == section]


def popular_cards() -> list[AnalysisCard]:
    return cards_in_section("popular")


def comparison_cards() -> list[AnalysisCard]:
    return cards_in_section("comparison")


def commune_cards() -> list[AnalysisCard]:
    return cards_in_section("commune")


def card_validation_issues() -> list[str]:
    """Flag cards that point at a missing concept or have no destination."""
    issues: list[str] = []
    seen: set[str] = set()
    for card in ANALYSIS_CARDS:
        if card.id in seen:
            issues.append(f"Duplicate analysis card id: {card.id}")
        seen.add(card.id)
        if not card.concept_id and not card.page:
            issues.append(f"{card.id} has neither a concept_id nor a page")
        if card.concept_id and get_concept(card.concept_id) is None:
            issues.append(f"{card.id} points at unknown concept {card.concept_id!r}")
        if card.page and not card.page.startswith("pages/"):
            issues.append(f"{card.id} has a suspicious page path {card.page!r}")
    return issues

"""Public-interest priorities and source-backed question cards.

This module is deliberately deterministic. It does not read news at runtime and
does not generate text. The priorities reflect current Luxembourg public
interest themes checked against STATEC/public reporting in May 2026 and are
used to order home-page questions and mapping reports.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.concepts import get_concept
from src.data.source_catalog import search_source_catalog


@dataclass(frozen=True)
class PriorityTopic:
    name: str
    category: str
    keywords: tuple[str, ...]
    weight: int


@dataclass(frozen=True)
class QuestionTemplate:
    id: str
    question: str
    description: str
    topic: str
    keywords: tuple[str, ...]
    page: str
    concept_id: str | None = None


PRIORITY_TOPICS: tuple[PriorityTopic, ...] = (
    PriorityTopic("Housing", "Housing", ("housing", "prices", "rent", "construction", "building permits"), 100),
    PriorityTopic("Prices & Inflation", "Prices / Inflation", ("inflation", "consumer prices", "indexation", "cost of living"), 95),
    PriorityTopic("Labour Market", "Labour Market", ("unemployment", "jobseekers", "vacancies", "employment"), 90),
    PriorityTopic("Population", "Population", ("population", "migration", "ageing", "fertility", "commune"), 85),
    PriorityTopic("Salaries", "Salaries / Income", ("salary", "income", "wages", "minimum wage", "distribution"), 80),
    PriorityTopic("Economy", "Economy / National Accounts", ("gdp", "confidence", "short-term", "business"), 65),
    PriorityTopic("Environment / Energy", "Environment / Energy", ("energy", "environment", "emissions", "prices"), 45),
    PriorityTopic("Tourism", "Tourism", ("tourism", "hotels", "overnight stays"), 35),
    PriorityTopic("Transport", "Transport", ("transport", "traffic", "mobility"), 35),
    PriorityTopic("Public Finance", "Public Finance", ("budget", "tax", "public finance"), 30),
)


QUESTION_TEMPLATES: tuple[QuestionTemplate, ...] = (
    QuestionTemplate(
        "housing_prices",
        "How are housing prices changing?",
        "Track official house-price and apartment-price trends.",
        "Housing",
        ("housing prices", "house price index", "apartment prices"),
        "pages/6_Housing.py",
        "house_price_index",
    ),
    QuestionTemplate(
        "housing_supply",
        "Is construction recovering?",
        "Follow building permits and new housing supply.",
        "Housing",
        ("construction", "building permits", "new homes"),
        "pages/6_Housing.py",
        "new_homes",
    ),
    QuestionTemplate(
        "salary_sectors",
        "Which sectors pay the most?",
        "Rank sectors by average yearly salary.",
        "Salaries",
        ("salary sector", "wages", "income"),
        "pages/7_Salaries.py",
        "salary_by_sector",
    ),
    QuestionTemplate(
        "inflation",
        "How is inflation changing?",
        "See the yearly change in consumer prices.",
        "Prices & Inflation",
        ("inflation", "consumer prices", "cost of living"),
        "pages/10_Prices_Inflation.py",
        "inflation_rate",
    ),
    QuestionTemplate(
        "unemployment",
        "Is unemployment rising?",
        "Compare employment and unemployment over time.",
        "Labour Market",
        ("unemployment", "jobs", "employment"),
        "pages/9_Labour_Market.py",
        "jobs_unemployment",
    ),
    QuestionTemplate(
        "population_growth",
        "How fast is Luxembourg's population growing?",
        "Track population growth and resident nationality groups.",
        "Population",
        ("population", "growth", "residents"),
        "pages/8_Population.py",
        "population_growth",
    ),
    QuestionTemplate(
        "commune_profile",
        "How does my commune compare?",
        "Open a local profile with mapped commune-level metrics.",
        "Communes",
        ("commune", "municipality", "local"),
        "pages/3_Commune_Portal.py",
        None,
    ),
    QuestionTemplate(
        "newest_statistics",
        "What are the newest STATEC statistics?",
        "Review recently refreshed metrics and publication annexes.",
        "Updates",
        ("latest", "new", "publication", "updated"),
        "pages/5_What_Changed.py",
        None,
    ),
)


def priority_for_category(category: str) -> int:
    for topic in PRIORITY_TOPICS:
        if topic.category == category or topic.name == category:
            return topic.weight
    return 10


def home_question_cards(limit: int = 8) -> list[dict[str, object]]:
    """Source-backed home cards ordered by public-interest priority."""
    cards: list[dict[str, object]] = []
    for template in QUESTION_TEMPLATES:
        sources: list[dict] = []
        for keyword in template.keywords:
            sources.extend(search_source_catalog(keyword, {"category": _category_for_topic(template.topic)}))
        deduped = {source["source_id"]: source for source in sources}.values()
        concept = get_concept(template.concept_id) if template.concept_id else None
        chart_ready = concept is not None
        cards.append(
            {
                "id": template.id,
                "question": template.question,
                "description": template.description,
                "topic": template.topic,
                "page": template.page,
                "concept_id": template.concept_id,
                "chart_ready": chart_ready,
                "source_count": len(list(deduped)),
                "status": "Chart ready" if chart_ready else "Source available, chart mapping pending",
                "priority": priority_for_category(_category_for_topic(template.topic)),
            }
        )
    cards.sort(key=lambda item: (-int(item["chart_ready"]), -int(item["priority"]), -int(item["source_count"])))
    return cards[:limit]


def _category_for_topic(topic: str) -> str:
    return {
        "Housing": "Housing",
        "Salaries": "Salaries / Income",
        "Prices & Inflation": "Prices / Inflation",
        "Labour Market": "Labour Market",
        "Population": "Population",
        "Communes": "Communes / Geography",
        "Updates": "Other / Unknown",
    }.get(topic, topic)

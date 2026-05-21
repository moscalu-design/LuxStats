"""Curated concept layer: human-friendly statistics backed by real LUSTAT data.

Each :class:`Concept` maps an everyday question ("how fast is the population
growing?") to a confirmed STATEC / LUSTAT dataset plus enough chart
configuration to draw a clean, readable chart automatically.

Every ``dataset_id`` here was verified against the live LUSTAT SDMX API
(https://lustat.statec.lu/rest). These are confirmed IDs, not placeholders.
The unconfirmed/placeholder catalog still lives in ``src/catalog.py`` and powers
the advanced Dataset Explorer.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Concept:
    """One curated, ready-to-chart statistic."""

    id: str
    title: str                       # friendly, plain-language title
    description: str                 # one-sentence plain description
    topic: str                       # matches a portal topic
    keywords: list[str]              # everyday search words / synonyms
    dataset_id: str                  # confirmed LUSTAT dataflow id
    chart: str = "line"              # "line" or "ranked_bar"
    value_format: str = "number"     # see src/formatting.VALUE_FORMATS
    explanation: str = ""            # "what this chart means" copy
    series_dim: str | None = None    # SDMX dimension used to split series
    default_series: list[str] = field(default_factory=list)  # series labels to show
    series_labels: dict[str, str] = field(default_factory=dict)  # raw -> friendly
    filters: dict[str, str] = field(default_factory=dict)    # fixed dimension filters
    freq: str | None = None          # FREQ_LABEL value to keep (e.g. "Annual")
    transform: str | None = None     # None or "yoy" (year-over-year % change)
    unit_note: str = ""              # short note about the unit shown
    caveat: str = ""                 # honest caveat about the data
    recommended: bool = True
    popular: bool = False            # show on the home "popular charts" row
    difficulty: str = "beginner"     # "beginner" or "intermediate"
    geographic_level: str = "national"  # national / commune / region / unknown

    @property
    def search_text(self) -> str:
        return " ".join(
            [self.title, self.description, self.topic, " ".join(self.keywords)]
        ).lower()

    @property
    def chart_label(self) -> str:
        """Plain-language name of the recommended chart type."""
        return {
            "line": "Trend line",
            "ranked_bar": "Ranking",
            "bar": "Bar chart",
        }.get(self.chart, "Chart")


# --------------------------------------------------------------------------
# Curated concepts. dataset_id values confirmed live against LUSTAT.
# --------------------------------------------------------------------------

CONCEPTS: list[Concept] = [
    Concept(
        id="population_growth",
        title="Luxembourg's population over time",
        description="How many people live in Luxembourg, and how the split between "
        "Luxembourgers and foreign residents has changed.",
        topic="Population",
        keywords=["population", "people", "residents", "growth", "inhabitants",
                  "how many people", "demographics", "foreigners"],
        dataset_id="DF_B1115",
        chart="line",
        value_format="number",
        series_dim="SPECIFICATION",
        default_series=["Total population", "Luxembourgers", "Foreigners"],
        explanation="Each line shows the number of residents on 1 January. "
        "Luxembourg's population has grown steadily, and a large share of "
        "residents hold a foreign nationality.",
        unit_note="Number of residents on 1 January.",
        caveat="Counts people of usual residence. Historic years are included "
        "where STATEC publishes them.",
        recommended=True,
        popular=True,
    ),
    Concept(
        id="inflation_index",
        title="Consumer prices in Luxembourg",
        description="The national consumer price index — the standard measure of "
        "the cost of living.",
        topic="Prices & Inflation",
        keywords=["inflation", "prices", "cost of living", "cpi", "consumer price",
                  "price index", "expensive"],
        dataset_id="DSD_PRIX_CONSO@DF_E5100",
        chart="line",
        value_format="index",
        freq="Annual",
        explanation="The consumer price index tracks the average price of things "
        "households buy. A rising line means the cost of living is going up.",
        unit_note="Index, base 100 on 1 January 1948.",
        caveat="Shows the annual average index. Inflation is the year-to-year "
        "change in this index.",
        recommended=True,
        popular=True,
    ),
    Concept(
        id="inflation_rate",
        title="Luxembourg's inflation rate",
        description="How fast prices rose each year, in percent.",
        topic="Prices & Inflation",
        keywords=["inflation", "inflation rate", "prices rising", "cost of living",
                  "price increase", "how much inflation"],
        dataset_id="DSD_PRIX_CONSO@DF_E5100",
        chart="line",
        value_format="percent",
        freq="Annual",
        transform="yoy",
        explanation="This is the year-over-year change in consumer prices. "
        "Higher bars mean the cost of living rose faster that year.",
        unit_note="Yearly change in the consumer price index, in percent.",
        caveat="Derived from the annual consumer price index. The most recent "
        "year may still be partial.",
        recommended=True,
        popular=True,
    ),
    Concept(
        id="jobs_unemployment",
        title="Jobs and unemployment",
        description="How many people are employed and how many are looking for work.",
        topic="Labour Market",
        keywords=["unemployment", "jobs", "employment", "work", "labour", "labor",
                  "out of work", "job market", "working"],
        dataset_id="DF_B3010",
        chart="line",
        value_format="number",
        series_dim="SPECIFICATION",
        default_series=["7. National employment (3 + 5)", "9. Number of unemployed"],
        series_labels={
            "7. National employment (3 + 5)": "People employed",
            "9. Number of unemployed": "People unemployed",
        },
        explanation="Compares the number of people in work with the number "
        "registered as unemployed. The gap shows how healthy the job market is.",
        unit_note="Number of people (monthly figures, averaged by year).",
        caveat="National concept of employment. The latest year may cover only "
        "part of the year.",
        recommended=True,
        popular=True,
    ),
    Concept(
        id="salary_by_sector",
        title="Average yearly salary by sector",
        description="Compare typical full-time gross pay across industries.",
        topic="Salaries",
        keywords=["salary", "salaries", "wage", "wages", "pay", "income",
                  "earnings", "sector", "industry", "by sector", "how much do people earn"],
        dataset_id="DF_C1202",
        chart="ranked_bar",
        value_format="euro",
        series_dim="NACE_REV2",
        filters={"GENDER": "Total"},
        explanation="Each bar is the average gross yearly salary of full-time "
        "workers in that part of the economy, for the most recent year available.",
        unit_note="Average annual gross earnings, full-time workers, in euros.",
        caveat="Gross earnings before tax and social contributions. Sectors use "
        "the official NACE classification.",
        recommended=True,
        popular=True,
    ),
    Concept(
        id="gender_pay",
        title="Salaries: women and men",
        description="How average pay compares between women and men.",
        topic="Salaries",
        keywords=["gender pay gap", "women", "men", "salary", "equal pay",
                  "wage gap", "pay gap"],
        dataset_id="DF_C1202",
        chart="line",
        value_format="euro",
        series_dim="GENDER",
        default_series=["Men", "Women"],
        filters={"NACE_REV2": "Industry and services (B-S)"},
        explanation="Average gross yearly salary for women and men across "
        "industry and services. A gap between the lines is the gender pay gap.",
        unit_note="Average annual gross earnings, full-time workers, in euros.",
        caveat="Gross earnings for full-time workers in the whole economy "
        "(industry and services).",
        recommended=True,
        popular=False,
    ),
    Concept(
        id="minimum_wage",
        title="The minimum wage over time",
        description="How Luxembourg's legal minimum wage has changed.",
        topic="Salaries",
        keywords=["minimum wage", "lowest salary", "social minimum wage",
                  "smic", "minimum pay"],
        dataset_id="DF_C1201",
        chart="line",
        value_format="euro",
        series_dim="SPECIFICATION",
        default_series=["Unskilled adults (100 %)", "Qualified adults (120 %)"],
        series_labels={
            "Unskilled adults (100 %)": "Unskilled adults",
            "Qualified adults (120 %)": "Qualified adults",
        },
        explanation="The social minimum wage is the lowest legal monthly pay. "
        "Qualified workers are entitled to a higher rate than unskilled workers.",
        unit_note="Monthly social minimum wage, in euros.",
        caveat="Gross monthly amounts. Rates are indexed and updated periodically.",
        recommended=True,
        popular=False,
    ),
    Concept(
        id="new_homes",
        title="New homes approved each year",
        description="How many new dwellings get building permits — a sign of "
        "housing supply.",
        topic="Housing",
        keywords=["housing", "homes", "building permits", "construction",
                  "new dwellings", "houses built", "real estate", "property"],
        dataset_id="DF_D4111",
        chart="line",
        value_format="number",
        series_dim="PRODUCT_BCS",
        default_series=["Residential buildings"],
        freq="Annual",
        explanation="Building permits show how many new homes are cleared for "
        "construction. More permits usually means more housing supply ahead.",
        unit_note="Number of dwellings authorised by building permits.",
        caveat="Permits are an early signal of supply; not every permit becomes "
        "a finished home.",
        recommended=True,
        popular=False,
    ),
    Concept(
        id="home_size",
        title="The size of new homes",
        description="How large newly built homes are, on average.",
        topic="Housing",
        keywords=["housing", "home size", "apartment size", "square metres",
                  "dwelling size", "how big are homes", "property"],
        dataset_id="DF_D4202",
        chart="line",
        value_format="m2",
        series_dim="SPECIFICATION",
        default_series=["Total", "Apartment houses", "One dwelling residential buildings"],
        series_labels={
            "Total": "All new homes",
            "Apartment houses": "Apartments",
            "One dwelling residential buildings": "Single-family houses",
        },
        explanation="The average floor area of residential dwellings, by the "
        "year they were completed. It shows whether new homes are getting "
        "bigger or smaller.",
        unit_note="Average usable floor area, in square metres.",
        caveat="Average size by year of completion of the building.",
        recommended=True,
        popular=False,
    ),
]

CONCEPTS_BY_ID: dict[str, Concept] = {c.id: c for c in CONCEPTS}


def all_concepts() -> list[Concept]:
    return list(CONCEPTS)


def get_concept(concept_id: str) -> Concept | None:
    return CONCEPTS_BY_ID.get(concept_id)


def concepts_for_topic(topic: str) -> list[Concept]:
    return [c for c in CONCEPTS if c.topic == topic]


def popular_concepts() -> list[Concept]:
    return [c for c in CONCEPTS if c.popular]


def topics_with_concepts() -> list[str]:
    seen: list[str] = []
    for concept in CONCEPTS:
        if concept.topic not in seen:
            seen.append(concept.topic)
    return seen

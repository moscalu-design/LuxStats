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

from src.data.excel_sources import AVERAGE_PRICES_ID, HOUSE_PRICE_INDEX_ID


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
        id="house_price_index",
        title="House prices over time",
        description="The official house price index — how the cost of buying "
        "a home has changed, for houses and apartments.",
        topic="Housing",
        keywords=["housing prices", "house prices", "property prices", "home prices",
                  "real estate prices", "cost of buying a home", "price index",
                  "housing market", "what are housing prices doing", "expensive homes"],
        dataset_id=HOUSE_PRICE_INDEX_ID,
        chart="line",
        value_format="index",
        series_dim="SPECIFICATION",
        default_series=["All dwellings", "Existing houses", "Existing apartments",
                        "New dwellings"],
        explanation="The house price index tracks how much homes cost to buy, "
        "with 2015 set to 100. A rising line means homes are getting more "
        "expensive. Prices fell sharply in 2023 before levelling off.",
        unit_note="Price index, base 100 in 2015. Quarterly figures, averaged by year.",
        caveat="Official STATEC acquisition-price statistics for dwellings "
        "(publication D4011). Quarterly data is averaged to a yearly figure "
        "here; quarterly detail is in the advanced view.",
        recommended=True,
        popular=True,
    ),
    Concept(
        id="apartment_prices",
        title="Average apartment prices",
        description="The average price of buying an apartment in Luxembourg, "
        "in euros.",
        topic="Housing",
        keywords=["apartment prices", "flat prices", "how much is an apartment",
                  "property prices", "housing prices", "cost of an apartment",
                  "real estate", "buy a flat", "apartment cost"],
        dataset_id=AVERAGE_PRICES_ID,
        chart="line",
        value_format="euro",
        series_dim="SPECIFICATION",
        default_series=["All apartments", "Existing apartments", "New apartments"],
        explanation="The average sale price of an apartment, across all sizes. "
        "‘New’ apartments are sold before or during construction; ‘existing’ "
        "apartments are resales.",
        unit_note="Average sale price in euros, all apartment sizes combined. "
        "Quarterly figures, averaged by year.",
        caveat="Official STATEC acquisition-price statistics (publication "
        "D4011). An average mixes small and large apartments, so it moves with "
        "the size mix as well as with prices.",
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
    Concept(
        id="permits_by_canton",
        title="New homes approved, by canton",
        description="Where Luxembourg is clearing new dwellings for construction — "
        "building permits by canton.",
        topic="Housing",
        keywords=["building permits", "construction", "new homes", "canton",
                  "housing supply", "where is housing being built", "permits by region",
                  "new dwellings", "real estate"],
        dataset_id="DF_D4113",
        chart="ranked_bar",
        value_format="number",
        series_dim="CANTON",
        filters={"PRODUCT_BCS": "Residential buildings"},
        freq="Annual",
        explanation="Each bar counts the dwellings authorised by building permits in "
        "that canton in the most recent year. Cantons with more permits are adding "
        "more housing supply.",
        unit_note="Number of dwellings authorised by building permits, residential "
        "buildings, most recent year available.",
        caveat="Permits are an early signal of supply; not every permit becomes a "
        "finished home. ‘Luxembourg city’ is reported separately from the rest of "
        "Canton Luxembourg.",
        recommended=True,
        popular=False,
        geographic_level="region",
    ),
    Concept(
        id="fertility_rate",
        title="How many children per woman",
        description="Luxembourg's total fertility rate — the average number of "
        "children a woman would have over her lifetime.",
        topic="Population",
        keywords=["fertility", "birth rate", "children per woman",
                  "total fertility rate", "births", "babies", "how many children"],
        dataset_id="DF_B2207",
        chart="line",
        value_format="rate",
        series_dim="SPECIFICATION",
        default_series=["Total population", "Luxembourgers", "Foreigners"],
        series_labels={"Total population": "All residents"},
        freq="Annual",
        explanation="The total fertility rate is the average number of children per "
        "woman. A rate of about 2.1 keeps a population stable without migration; "
        "Luxembourg has been below that for decades.",
        unit_note="Average number of children per woman (total fertility rate).",
        caveat="Before 2010 the breakdown follows the nationality of the child; "
        "from 2010 it follows the nationality of the mother.",
        recommended=True,
        popular=False,
    ),
    Concept(
        id="wage_indexation",
        title="Wage rises from automatic indexation",
        description="How much the automatic wage indexation added to salaries and "
        "pensions each year.",
        topic="Prices & Inflation",
        keywords=["indexation", "wage indexation", "échelle mobile", "index tranche",
                  "cote d'application", "salary index", "cost of living adjustment",
                  "tranche indiciaire", "indexed wages"],
        dataset_id="DSD_PRIX_EMS@DF_E5200",
        chart="line",
        value_format="percent",
        freq="Annual",
        filters={"UNIT_MEASURE": "Annual variation"},
        explanation="Luxembourg links pay to consumer prices. When average prices "
        "rise 2.5 % since the last adjustment, an index ‘tranche’ is triggered and "
        "salaries and pensions rise automatically. This shows the resulting wage "
        "increase each year — higher points mean indexation lifted pay more.",
        unit_note="Wage increase due to the automatic wage indexation, in percent "
        "per year.",
        caveat="Annual figure. It reflects past, published index adjustments and is "
        "not a forecast of future indexation.",
        recommended=True,
        popular=False,
    ),
    Concept(
        id="vacancies_jobseekers",
        title="Job vacancies and jobseekers",
        description="Job vacancies received by ADEM compared with the number of "
        "people registered as unemployed.",
        topic="Labour Market",
        keywords=["job vacancies", "jobseekers", "vacancies", "adem", "unemployed",
                  "job offers", "unfilled vacancies", "is it hard to find a job",
                  "labour demand"],
        dataset_id="DF_B3201",
        chart="line",
        value_format="number",
        series_dim="SPECIFICATION",
        default_series=["Job vacancies received by ADEM", "Unfilled vacancies",
                        "Unemployed"],
        series_labels={
            "Job vacancies received by ADEM": "Vacancies received (ADEM)",
            "Unfilled vacancies": "Unfilled vacancies",
            "Unemployed": "Registered unemployed",
        },
        freq="Annual",
        explanation="More vacancies and fewer jobseekers point to a tighter job "
        "market. The gap between unfilled vacancies and registered unemployed shows "
        "how well the two sides of the market match.",
        unit_note="Annual figures: job vacancies notified to ADEM and people "
        "registered as unemployed.",
        caveat="Covers vacancies notified to the public employment service (ADEM); "
        "not every job is advertised through ADEM.",
        recommended=True,
        popular=False,
    ),
    Concept(
        id="gdp_trend",
        title="The size of Luxembourg's economy",
        description="Gross domestic product (GDP) in real terms — the total value "
        "of what the economy produces.",
        topic="Economy",
        keywords=["gdp", "economy", "gross domestic product", "economic growth",
                  "output", "national accounts", "how big is the economy",
                  "recession"],
        dataset_id="DF_E2601",
        chart="line",
        value_format="number",
        series_dim="LABELS",
        default_series=["Gross domestic product at market prices (B1*G)"],
        series_labels={
            "Gross domestic product at market prices (B1*G)": "GDP (real terms)",
        },
        explanation="GDP measures the total value of goods and services produced in "
        "Luxembourg. It is shown here in real terms (chain-linked volumes), so the "
        "trend reflects real growth rather than rising prices.",
        unit_note="Quarterly GDP, chain-linked volumes (reference year 2015), in "
        "million euros. The four quarters of each year are averaged to one point.",
        caveat="Official STATEC quarterly national accounts. Quarterly figures are "
        "averaged to a yearly point here; the most recent year may still be revised.",
        recommended=True,
        popular=False,
        difficulty="intermediate",
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

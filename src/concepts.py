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

from src.data.excel_sources import AVERAGE_PRICES_ID, HOUSE_PRICE_INDEX_ID, TOURISM_ACTIVITY_ID


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
    annual_aggregation: str = "mean" # "mean" or "sum" when collapsing sub-annual data
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
        id="tourism_accommodation_activity",
        title="Tourism accommodation activity",
        description="Monthly arrivals and overnight stays in Luxembourg tourist accommodation, shown as annual totals.",
        topic="Tourism",
        keywords=[
            "tourism", "tourist", "tourists", "arrivals", "accommodation",
            "hotels", "overnight stays", "nights", "hotel activity",
            "tourism activity", "luxembourg tourism", "D5310",
        ],
        dataset_id=TOURISM_ACTIVITY_ID,
        chart="line",
        value_format="number",
        series_dim="SPECIFICATION",
        default_series=["Arrivals", "Overnight stays"],
        annual_aggregation="sum",
        explanation="The lines sum the monthly official counts across published tourist regions and accommodation types. Arrivals count guests; overnight stays count nights spent.",
        unit_note="Annual total count, summed from monthly STATEC D5310 rows.",
        caveat="Monthly figures are provisional until definitive annual results are calculated. The source workbook groups some camping regions differently from hotels.",
        recommended=True,
        popular=False,
        geographic_level="region",
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
    Concept(
        id="net_migration",
        title="People moving in and out of Luxembourg",
        description="Arrivals, departures and net migration — the main driver of "
        "Luxembourg's population growth.",
        topic="Population",
        keywords=["migration", "immigration", "emigration", "net migration",
                  "arrivals", "departures", "people moving", "newcomers",
                  "moving to Luxembourg"],
        dataset_id="DF_B2400",
        chart="line",
        value_format="number",
        series_dim="POP_MOVEMENT",
        default_series=["Arrivals", "Departures", "Net migration"],
        filters={"SPECIFICATION": "All citizenships"},
        explanation="Arrivals are people moving to Luxembourg, departures are people "
        "leaving, and net migration is the difference. Net migration has long been "
        "the main reason the population keeps growing.",
        unit_note="Number of people per year, all citizenships combined.",
        caveat="Counts moves across the national border recorded in population "
        "statistics; the most recent year may still be partial.",
        recommended=True,
        popular=False,
    ),
    Concept(
        id="births_deaths",
        title="Births and deaths each year",
        description="How often people are born and die in Luxembourg, as a rate per "
        "1,000 residents.",
        topic="Population",
        keywords=["births", "deaths", "birth rate", "death rate", "natural increase",
                  "mortality", "how many babies", "how many deaths"],
        dataset_id="DF_B2110",
        chart="line",
        value_format="rate",
        series_dim="SPECIFICATION",
        default_series=["Birth rate (in ‰)", "Death rate (en ‰)"],
        series_labels={
            "Birth rate (in ‰)": "Birth rate",
            "Death rate (en ‰)": "Death rate",
        },
        explanation="The birth and death rates are shown per 1,000 residents. When "
        "the birth rate sits above the death rate, the population grows on its own — "
        "before migration is counted.",
        unit_note="Births and deaths per 1,000 residents per year.",
        caveat="Crude rates: they are not adjusted for the age structure of the "
        "population.",
        recommended=True,
        popular=False,
    ),
    Concept(
        id="employment_by_sector",
        title="Where people work",
        description="Salaried jobs in Luxembourg split across the main parts of the "
        "economy.",
        topic="Labour Market",
        keywords=["employment", "jobs by sector", "where people work", "industries",
                  "payroll", "sectors", "workforce", "which industries employ most"],
        dataset_id="DSD_EMPLOI_SAL@DF_B3000",
        chart="ranked_bar",
        value_format="number",
        series_dim="ACTIVITY",
        default_series=[
            "Industry (except construction)",
            "Construction",
            "Wholesale and retail trade, transportation and storage, accommodation "
            "and food service activities",
            "Information and communication",
            "Financial and insurance activities",
            "Professional, scientific, technical, administrative and support "
            "service activities",
            "Public administration, defence, education, human health and social "
            "work activities",
            "Other activities",
        ],
        series_labels={
            "Industry (except construction)": "Industry",
            "Wholesale and retail trade, transportation and storage, accommodation "
            "and food service activities": "Trade, transport & hospitality",
            "Information and communication": "Information & communication",
            "Financial and insurance activities": "Finance & insurance",
            "Professional, scientific, technical, administrative and support "
            "service activities": "Business services",
            "Public administration, defence, education, human health and social "
            "work activities": "Public sector, education & health",
        },
        filters={"ADJUSTMENT": "Calendar and seasonally adjusted data"},
        explanation="Each bar is the number of salaried jobs in that part of the "
        "economy in the most recent year. It shows which sectors employ the most "
        "people.",
        unit_note="Domestic payroll (salaried) employment, most recent year. "
        "Quarterly figures averaged by year.",
        caveat="Covers salaried employment only, not the self-employed. Sectors "
        "group the official NACE classification.",
        recommended=True,
        popular=False,
    ),
    Concept(
        id="pay_by_education",
        title="How education affects pay",
        description="Average monthly earnings by the level of education a worker "
        "completed.",
        topic="Salaries",
        keywords=["education", "pay by education", "does education pay", "earnings",
                  "qualifications", "degree", "salary by education level"],
        dataset_id="DSD_ESS_EARN_M@DF_C1217",
        chart="ranked_bar",
        value_format="euro",
        series_dim="EDUC_LEVEL",
        default_series=[
            "Low -  basic level (primary or secondary not completed)",
            "Medium - completed secondary education (vocational, technician, "
            "technical or baccalaureate, etc.)",
            "High - tertiary level (BTS, bachelor, master, doctorate, etc.)",
        ],
        series_labels={
            "Low -  basic level (primary or secondary not completed)":
                "Basic education",
            "Medium - completed secondary education (vocational, technician, "
            "technical or baccalaureate, etc.)": "Secondary education",
            "High - tertiary level (BTS, bachelor, master, doctorate, etc.)":
                "Higher education",
        },
        filters={
            "NACE_R2": "Total - all NACE activities",
            "MEASURE": "Average monthly earnings, full-time equivalent",
        },
        explanation="Each bar is the average monthly full-time salary for workers "
        "with that level of education, across the whole economy. Higher education "
        "generally means higher pay.",
        unit_note="Average gross monthly earnings, full-time equivalent, in euros.",
        caveat="From STATEC's structure-of-earnings survey, run every four years; "
        "the most recent year available is 2022.",
        recommended=True,
        popular=False,
    ),
    Concept(
        id="gva_by_sector",
        title="What Luxembourg's economy produces",
        description="Gross value added by sector — which parts of the economy "
        "generate the most output.",
        topic="Economy",
        keywords=["value added", "sectors", "economy by sector", "gva",
                  "what the economy produces", "industries", "economic structure"],
        dataset_id="DF_E2601",
        chart="ranked_bar",
        value_format="number",
        series_dim="LABELS",
        default_series=[
            "Agriculture, forestry and fishing (A)",
            "Industry, including energy and water supply (B_E)",
            "Construction (F)",
            "Trade, repair of motor vehicles, transportation and stroage, hotels "
            "and restaurants  (G_I)",
            "Information and communication (J)",
            "Financial and insurance activities (K)",
            "Real estate activities (L)",
            "Business activities and renting (M_N)",
            "Public administration, social security, education, health and social "
            "work activities (O_Q)",
            "Entertainment and recreation, repair of household goods and other "
            "services (R_U)",
        ],
        series_labels={
            "Agriculture, forestry and fishing (A)": "Agriculture",
            "Industry, including energy and water supply (B_E)": "Industry & energy",
            "Construction (F)": "Construction",
            "Trade, repair of motor vehicles, transportation and stroage, hotels "
            "and restaurants  (G_I)": "Trade, transport & hospitality",
            "Information and communication (J)": "Information & communication",
            "Financial and insurance activities (K)": "Finance & insurance",
            "Real estate activities (L)": "Real estate",
            "Business activities and renting (M_N)": "Business services",
            "Public administration, social security, education, health and social "
            "work activities (O_Q)": "Public sector, education & health",
            "Entertainment and recreation, repair of household goods and other "
            "services (R_U)": "Other services",
        },
        explanation="Gross value added measures the output each sector adds to the "
        "economy. Finance and business services dominate Luxembourg's output.",
        unit_note="Gross value added, chain-linked volumes (reference year 2015), "
        "in million euros. Quarterly figures averaged by year.",
        caveat="Official STATEC quarterly national accounts. The ten sectors "
        "together make up total value added.",
        recommended=True,
        popular=False,
        difficulty="intermediate",
    ),
    Concept(
        id="prices_by_category",
        title="Inflation by spending category",
        description="How fast prices rose each year in the main parts of the "
        "household budget.",
        topic="Prices & Inflation",
        keywords=["inflation by category", "food prices", "energy prices",
                  "cost of living", "price categories", "what got more expensive",
                  "services prices"],
        dataset_id="DSD_ECOICOP_PRIX@DF_E5409",
        chart="line",
        value_format="percent",
        series_dim="ECOICOP_2018",
        default_series=["All Items", "Food, including alcohol and tobacco",
                        "Energy", "Non-energy industrial goods", "Services"],
        series_labels={
            "Food, including alcohol and tobacco": "Food",
            "Non-energy industrial goods": "Goods (non-energy)",
        },
        transform="yoy",
        explanation="Each line is the yearly change in consumer prices for that "
        "category. Energy is the most volatile — it spiked sharply in 2022 — while "
        "services prices tend to rise more steadily.",
        unit_note="Yearly change in the national consumer price index, by category, "
        "in percent.",
        caveat="Derived from the monthly national CPI (ECOICOP categories), "
        "averaged by year. The most recent year may still be partial.",
        recommended=True,
        popular=False,
    ),
    Concept(
        id="services_confidence",
        title="Business confidence in services",
        description="How optimistic services companies feel about their business — "
        "an early signal of where the economy is heading.",
        topic="Economy",
        keywords=["business confidence", "economic sentiment", "services confidence",
                  "outlook", "economic mood", "conjuncture", "short-term indicator"],
        dataset_id="DSD_ENT_CONJ@DF_D5105",
        chart="line",
        value_format="number",
        filters={"MEASURE": "Services confidence indicator"},
        explanation="The services confidence indicator summarises how firms judge "
        "recent and expected demand. Positive values mean optimism, negative values "
        "mean pessimism; it tends to dip before economic slowdowns.",
        unit_note="Services confidence indicator, balance of opinion. Monthly "
        "figures averaged by year.",
        caveat="Based on STATEC's monthly business opinion survey of services "
        "firms; it measures sentiment, not output.",
        recommended=True,
        popular=False,
        difficulty="intermediate",
    ),
    Concept(
        id="cross_border_workers",
        title="Residents and cross-border workers",
        description="How many of Luxembourg's salaried jobs are held by residents "
        "and how many by workers commuting in from abroad.",
        topic="Labour Market",
        keywords=["cross-border workers", "frontaliers", "commuters", "residents",
                  "workforce", "who works in Luxembourg", "border workers"],
        dataset_id="DSD_EMPLOI_SAL@DF_B3002",
        chart="line",
        value_format="number",
        series_dim="RESIDENCE",
        default_series=["Total residents", "Total cross-border"],
        filters={"ADJUSTMENT": "Calendar and seasonally adjusted data"},
        explanation="Luxembourg's workforce is split between people who live in the "
        "country and cross-border workers who commute in daily from Belgium, France "
        "and Germany. Cross-border workers make up a large share of all jobs.",
        unit_note="Domestic payroll (salaried) employment, number of people. "
        "Quarterly figures averaged by year.",
        caveat="Covers salaried employment only. The cross-border total combines "
        "commuters from Belgium, France and Germany.",
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

"""Curated dataset catalog and search helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from src.config import THEME_ORDER


TODO_DATASET_PREFIX = "TODO_CONFIRM_"


@dataclass(frozen=True)
class CatalogEntry:
    dataset_id: str
    theme: str
    title: str
    friendly_title: str
    description: str
    keywords: list[str] = field(default_factory=list)
    dimensions: list[str] = field(default_factory=list)
    time_periods: str = "Load the dataset to inspect available periods."
    geography: str = "Unknown until dataset metadata is loaded."
    update_frequency: str = "Check STATEC / LUSTAT metadata."
    recommended: bool = False
    dashboard: str | None = None
    notes: str = ""
    status: str = "needs_confirmation"
    geographic_level: str = "unknown"
    geography_column: str | None = None
    commune_code_column: str | None = None
    commune_name_column: str | None = None
    value_column: str = "OBS_VALUE"
    time_column: str = "TIME_PERIOD"
    commune_portal: bool = False
    default_filters: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "theme": self.theme,
            "title": self.title,
            "friendly_title": self.friendly_title,
            "description": self.description,
            "keywords": self.keywords,
            "dimensions": self.dimensions,
            "time_periods": self.time_periods,
            "geography": self.geography,
            "update_frequency": self.update_frequency,
            "recommended": self.recommended,
            "dashboard": self.dashboard,
            "notes": self.notes,
            "status": self.status,
            "geographic_level": self.geographic_level,
            "geography_column": self.geography_column,
            "commune_code_column": self.commune_code_column,
            "commune_name_column": self.commune_name_column,
            "value_column": self.value_column,
            "time_column": self.time_column,
            "commune_portal": self.commune_portal,
            "default_filters": self.default_filters,
        }


STARTER_CATALOG: list[CatalogEntry] = [
    CatalogEntry(
        dataset_id="TODO_CONFIRM_SALARY",
        theme="Salaries",
        title="Salary and wage datasets",
        friendly_title="Salaries and wages",
        description="Compare pay by year, sector, occupation, sex, education, or other available breakdowns.",
        keywords=["salary", "salaries", "wage", "wages", "income", "pay", "sector", "occupation", "decile"],
        dimensions=["Year", "Sector", "Occupation", "Sex", "Education", "Salary band or decile"],
        time_periods="Depends on selected salary dataflow.",
        geography="National, with commune-level views if available in the selected dataflow.",
        recommended=True,
        dashboard="Salaries",
        notes="Use the Salaries page to search live LUSTAT dataflows. Replace this placeholder with confirmed dataset IDs as dashboards are curated.",
    ),
    CatalogEntry(
        dataset_id="DSD_CENSUS_NB_LOG_CLA@DF_B1707",
        theme="Housing",
        title="Dwellings by commune",
        friendly_title="Dwellings by commune",
        description="Count standard dwellings by commune from the 2021 population census.",
        keywords=["housing", "dwellings", "homes", "census", "commune", "municipality", "real estate", "property"],
        dimensions=["Year", "Commune", "Building type", "Occupancy status"],
        time_periods="2021 census.",
        geography="Commune.",
        recommended=True,
        dashboard="Housing",
        notes="Confirmed LUSTAT census table. It counts dwellings, not sale prices or rents.",
        status="confirmed",
        geographic_level="commune",
        geography_column="GEO_LABEL",
        commune_code_column="GEO",
        commune_name_column="GEO_LABEL",
        commune_portal=True,
        default_filters={"TYPE_BUILD_DWE": "_T", "OCC_STATUS_CONV": "_T"},
    ),
    CatalogEntry(
        dataset_id="TODO_CONFIRM_RENTS",
        theme="Housing",
        title="Rents",
        friendly_title="Rents",
        description="Explore rent levels and changes over time where official datasets are available.",
        keywords=["rent", "rents", "rental", "housing", "affordability"],
        dimensions=["Year", "Commune or region", "Dwelling size or type", "Rent metric"],
        time_periods="Needs confirmation from LUSTAT metadata.",
        geography="Commune or region if available.",
        recommended=True,
        dashboard="Housing",
        notes="Exact LUSTAT dataflow ID still needs confirmation.",
        geographic_level="commune",
        geography_column="Commune",
        commune_name_column="Commune",
        commune_portal=True,
    ),
    CatalogEntry(
        dataset_id="DF_X021",
        theme="Population",
        title="Population by commune",
        friendly_title="Population by commune",
        description="See how Luxembourg's population changes over time nationally and by commune.",
        keywords=["people", "residents", "population", "commune", "municipality", "growth"],
        dimensions=["Year", "Commune"],
        time_periods="1821 onward where available.",
        geography="Commune.",
        recommended=True,
        dashboard="Population",
        notes="Confirmed LUSTAT table: Population by canton and municipality.",
        status="confirmed",
        geographic_level="commune",
        geography_column="CANTON_LABEL",
        commune_code_column="CANTON",
        commune_name_column="CANTON_LABEL",
        commune_portal=True,
    ),
    CatalogEntry(
        dataset_id="DF_X020",
        theme="Population",
        title="Population density by commune",
        friendly_title="Population density",
        description="Population density by commune, in inhabitants per square kilometre.",
        keywords=["population", "density", "commune", "municipality", "inhabitants"],
        dimensions=["Year", "Commune"],
        time_periods="1821 onward where available.",
        geography="Commune.",
        recommended=True,
        dashboard="Population",
        notes="Confirmed LUSTAT table: Population density by canton and municipality on 1 January.",
        status="confirmed",
        geographic_level="commune",
        geography_column="CANTON_LABEL",
        commune_code_column="CANTON",
        commune_name_column="CANTON_LABEL",
        commune_portal=True,
    ),
    CatalogEntry(
        dataset_id="DF_C1600",
        theme="Salaries",
        title="Median monthly salaries by commune",
        friendly_title="Median monthly salary",
        description="Median monthly salary by commune where STATEC publishes municipality-level salary statistics.",
        keywords=["salary", "salaries", "wage", "wages", "pay", "commune", "municipality", "median"],
        dimensions=["Year", "Commune", "Indicator"],
        time_periods="2013 onward where available.",
        geography="Commune.",
        recommended=True,
        dashboard="Salaries",
        notes="Confirmed LUSTAT table: Monthly salaries by municipality. The Commune Portal uses the Median indicator.",
        status="confirmed",
        geographic_level="commune",
        geography_column="MUNICIPALITY_LABEL",
        commune_code_column="MUNICIPALITY",
        commune_name_column="MUNICIPALITY_LABEL",
        commune_portal=True,
        default_filters={"INDICATOR_LABEL": "Median"},
    ),
    CatalogEntry(
        dataset_id="DF_X026",
        theme="Labour Market",
        title="Unemployment rate by commune",
        friendly_title="Unemployment rate",
        description="Employment and unemployment indicators by commune.",
        keywords=["employment", "unemployment", "jobs", "work", "labour", "commune", "municipality"],
        dimensions=["Year", "Commune", "Indicator"],
        time_periods="2001 onward where available.",
        geography="Commune.",
        recommended=True,
        dashboard="Labour Market",
        notes="Confirmed LUSTAT table: Employment and unemployment by canton and municipality. STATEC notes that figures should be used carefully because source administrations define municipalities from postal codes, and some postal codes span several municipalities.",
        status="confirmed",
        geographic_level="commune",
        geography_column="SPECIFICATION_LABEL",
        commune_code_column="SPECIFICATION",
        commune_name_column="SPECIFICATION_LABEL",
        commune_portal=True,
        default_filters={"VARIABLE_LABEL": "Unemployment rate (in %)"},
    ),
    CatalogEntry(
        dataset_id="DSD_CENSUS_MENAGE_PV@DF_B1703",
        theme="Population",
        title="Private households by commune",
        friendly_title="Private households",
        description="Private households by commune of residence from the 2021 population census.",
        keywords=["households", "population", "census", "commune", "municipality"],
        dimensions=["Year", "Commune"],
        time_periods="2021 census.",
        geography="Commune.",
        recommended=True,
        dashboard="Population",
        notes="Confirmed LUSTAT census table: Private households by canton and municipality of residence.",
        status="confirmed",
        geographic_level="commune",
        geography_column="GEO_LABEL",
        commune_code_column="GEO",
        commune_name_column="GEO_LABEL",
        commune_portal=True,
        default_filters={"SIZE_PRV_HH": "_T"},
    ),
    CatalogEntry(
        dataset_id="TODO_CONFIRM_LABOUR_MARKET",
        theme="Labour Market",
        title="Employment and unemployment",
        friendly_title="Jobs and unemployment",
        description="Follow employment and unemployment indicators by time and available groups.",
        keywords=["employment", "unemployment", "jobs", "work", "labour", "labor"],
        dimensions=["Month or year", "Age group", "Sex", "Sector", "Geography"],
        time_periods="Needs confirmation from LUSTAT metadata.",
        geography="National, regional, or commune depending on dataflow.",
        recommended=True,
        dashboard="Labour Market",
        notes="Exact LUSTAT dataflow ID still needs confirmation.",
        geographic_level="unknown",
    ),
    CatalogEntry(
        dataset_id="TODO_CONFIRM_CPI",
        theme="Prices & Inflation",
        title="Consumer prices and inflation",
        friendly_title="Prices and inflation",
        description="Track how prices change over time and compare spending categories where available.",
        keywords=["inflation", "prices", "consumer price", "cpi", "index", "cost of living"],
        dimensions=["Month", "Spending category", "Index base", "Measure"],
        time_periods="Needs confirmation from LUSTAT metadata.",
        geography="National.",
        recommended=True,
        dashboard="Prices & Inflation",
        notes="Exact LUSTAT dataflow ID still needs confirmation.",
        geographic_level="national",
    ),
    CatalogEntry(
        dataset_id="TODO_CONFIRM_ECONOMY",
        theme="Economy",
        title="Business and economic indicators",
        friendly_title="Economy and business indicators",
        description="Follow headline economic indicators such as output, business activity, and sector trends where official datasets are available.",
        keywords=["economy", "business", "gdp", "activity", "companies", "sector", "indicator"],
        dimensions=["Quarter or year", "Sector", "Indicator", "Measure"],
        time_periods="Needs confirmation from LUSTAT metadata.",
        geography="National unless a selected dataflow supports regions.",
        recommended=True,
        dashboard="Economy",
        notes="Exact LUSTAT dataflow IDs still need confirmation.",
        geographic_level="national",
    ),
    CatalogEntry(
        dataset_id="TODO_CONFIRM_EDUCATION",
        theme="Education",
        title="Education indicators",
        friendly_title="Education",
        description="Explore students, education levels, and related indicators where official datasets are available.",
        keywords=["education", "school", "students", "university", "qualification", "diploma"],
        dimensions=["Year", "Education level", "Age group", "Sex", "Nationality"],
        time_periods="Needs confirmation from LUSTAT metadata.",
        geography="National, with commune-level views if available.",
        dashboard="Education",
        notes="Exact LUSTAT dataflow IDs still need confirmation.",
        geographic_level="unknown",
    ),
    CatalogEntry(
        dataset_id="TODO_CONFIRM_MOBILITY",
        theme="Mobility",
        title="Mobility and transport",
        friendly_title="Mobility and transport",
        description="Find transport and mobility indicators where official datasets are available.",
        keywords=["mobility", "transport", "traffic", "commute", "cars", "public transport"],
        dimensions=["Year", "Transport mode", "Geography", "Indicator"],
        time_periods="Needs confirmation from LUSTAT metadata.",
        geography="National or regional depending on dataflow.",
        dashboard="Mobility",
        notes="Exact LUSTAT dataflow IDs still need confirmation.",
        geographic_level="unknown",
    ),
    CatalogEntry(
        dataset_id="TODO_CONFIRM_PUBLIC_FINANCE",
        theme="Public Finance",
        title="Public finance",
        friendly_title="Public finance",
        description="Explore public revenue, spending, and finance indicators where official datasets are available.",
        keywords=["public finance", "government", "budget", "tax", "spending", "revenue", "debt"],
        dimensions=["Year", "Government function", "Measure", "Unit"],
        time_periods="Needs confirmation from LUSTAT metadata.",
        geography="National.",
        dashboard="Public Finance",
        notes="Exact LUSTAT dataflow IDs still need confirmation.",
        geographic_level="national",
    ),
]


def catalog_dataframe() -> pd.DataFrame:
    return pd.DataFrame([entry.as_dict() for entry in STARTER_CATALOG])


def is_placeholder_dataset_id(dataset_id: str) -> bool:
    return str(dataset_id).startswith(TODO_DATASET_PREFIX)


def catalog_themes() -> list[str]:
    """Return visible catalog themes in the app's preferred order."""
    known = set(catalog_dataframe()["theme"].dropna().unique())
    ordered = [theme for theme in THEME_ORDER if theme in known]
    extras = sorted(known.difference(ordered))
    return ordered + extras


def catalog_validation_issues() -> list[str]:
    """Flag catalog metadata mistakes that can confuse users or future wiring."""
    issues: list[str] = []
    df = catalog_dataframe()
    duplicate_ids = sorted(df[df["dataset_id"].duplicated()]["dataset_id"].unique())
    for dataset_id in duplicate_ids:
        issues.append(f"Duplicate catalog dataset_id: {dataset_id}")

    unknown_themes = sorted(set(df["theme"]).difference(THEME_ORDER))
    for theme in unknown_themes:
        issues.append(f"Catalog theme is missing from THEME_ORDER: {theme}")

    for row in df.to_dict("records"):
        dataset_id = str(row["dataset_id"])
        status = str(row.get("status") or "")
        if is_placeholder_dataset_id(dataset_id) and status != "needs_confirmation":
            issues.append(f"{dataset_id} is a placeholder but status is {status!r}")
        if not is_placeholder_dataset_id(dataset_id) and status == "needs_confirmation":
            issues.append(f"{dataset_id} looks confirmed but still has needs_confirmation status")
    return issues


def search_catalog(query: str = "", theme: str | None = None, recommended_only: bool = False) -> pd.DataFrame:
    df = catalog_dataframe()
    if recommended_only:
        df = df[df["recommended"]]
    if theme and theme != "All":
        df = df[df["theme"] == theme]
    query = (query or "").strip().lower()
    if query:
        terms = [term for term in query.split() if term]

        def matches(row: pd.Series) -> bool:
            haystack = " ".join(
                [
                    str(row.get("dataset_id", "")),
                    str(row.get("theme", "")),
                    str(row.get("friendly_title", "")),
                    str(row.get("description", "")),
                    " ".join(row.get("keywords", []) or []),
                ]
            ).lower()
            return all(term in haystack for term in terms)

        df = df[df.apply(matches, axis=1)]
    return df.reset_index(drop=True)


def catalog_entry(dataset_id: str) -> dict[str, Any] | None:
    df = catalog_dataframe()
    match = df[df["dataset_id"] == dataset_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()

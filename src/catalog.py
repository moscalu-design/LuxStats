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
        dataset_id="TODO_CONFIRM_HOUSING_PRICES",
        theme="Housing",
        title="Housing prices",
        friendly_title="Housing prices",
        description="Track home prices and compare places or property types where official data supports it.",
        keywords=["housing", "house prices", "property prices", "real estate", "apartment", "commune"],
        dimensions=["Year", "Commune or region", "Property type", "Price metric"],
        time_periods="Needs confirmation from LUSTAT metadata.",
        geography="Commune or region if available.",
        recommended=True,
        dashboard="Housing",
        notes="Exact LUSTAT dataflow ID still needs confirmation.",
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
    ),
    CatalogEntry(
        dataset_id="TODO_CONFIRM_POPULATION_COMMUNE",
        theme="Population",
        title="Population by commune",
        friendly_title="Population by commune",
        description="See how Luxembourg's population changes over time nationally and by commune.",
        keywords=["people", "residents", "population", "commune", "municipality", "growth"],
        dimensions=["Year", "Commune", "Age group", "Sex", "Nationality"],
        time_periods="Needs confirmation from LUSTAT metadata.",
        geography="Commune.",
        recommended=True,
        dashboard="Population",
        notes="Exact LUSTAT dataflow ID still needs confirmation.",
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

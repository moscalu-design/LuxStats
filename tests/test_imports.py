from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_app_and_pages_parse() -> None:
    targets = [ROOT / "app.py", *sorted((ROOT / "pages").glob("*.py"))]
    assert targets
    for path in targets:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_all_pages_configure_streamlit_before_rendering() -> None:
    for path in sorted((ROOT / "pages").glob("*.py")):
        source = path.read_text(encoding="utf-8")
        assert "configure_page(" in source, f"{path.name} does not configure page metadata"


def test_commune_portal_page_exists() -> None:
    assert (ROOT / "pages" / "3_Commune_Portal.py").exists()


def test_new_modules_import_cleanly() -> None:
    import importlib

    for module in [
        "src.data.analysis_cards",
        "src.data.geography",
        "src.ui.cards",
        "src.ui.explanations",
        "src.ui.source_badges",
        "src.ui.maps",
        "src.ui.chart_builder",
        "src.analysis.comparison",
        "src.analysis.changes",
    ]:
        importlib.import_module(module)

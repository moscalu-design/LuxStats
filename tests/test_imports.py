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
    assert (ROOT / "pages" / "9_Commune_Portal.py").exists()

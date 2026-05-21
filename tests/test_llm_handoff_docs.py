from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_agent_handoff_docs_exist() -> None:
    for rel in ["AGENTS.md", "CLAUDE.md", "CODEX.md", "docs/LLM_HANDOFF.md", "docs/PROMPTING_GUIDE.md"]:
        assert (ROOT / rel).exists()


def test_handoff_docs_include_key_rules() -> None:
    handoff = (ROOT / "docs" / "LLM_HANDOFF.md").read_text(encoding="utf-8").lower()
    assert "deterministic" in handoff
    assert "no fake data" not in handoff or "fake" in handoff
    assert "validation" in handoff
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8").lower()
    assert "do not add any llm" in agents
    assert "source visualization" in agents

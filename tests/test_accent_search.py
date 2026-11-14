"""Lexical search ignores accents and case, in the query and in the notes.

An office types "legislacao" as often as "Legislação"; both must find the same
note, whether the accent is in the body, the title or the query. CJK search
keeps working because the folding leaves CJK, kana and hangul runs alone.
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "integrations" / "obsidian-mcp-server"))

import vault_ops  # noqa: E402


@pytest.fixture()
def vault(tmp_path, monkeypatch):
    v = tmp_path / "cofre"
    (v / "Legislação").mkdir(parents=True)
    monkeypatch.setenv(vault_ops._VAULT_ENV, str(v))
    return v


def _paths(query: str) -> list[str]:
    return [r["path"] for r in vault_ops.search(query, semantic=False)]


def test_fold_basics():
    assert vault_ops._fold("Legislação Vigência AÇÃO") == "legislacao vigencia acao"
    assert vault_ops._fold("plain ASCII") == "plain ascii"
    # decomposed (macOS file names) and precomposed spellings fold the same
    assert vault_ops._fold(unicodedata.normalize("NFD", "Decisão")) == "decisao"
    # CJK, kana voiced marks and hangul syllables are untouched
    for s in ("知識管理", "がぎぐ", "한국어"):
        assert vault_ops._fold(s) == s


@pytest.mark.parametrize("query", ["legislacao", "Legislação", "LEGISLAÇÃO", "vigencia", "vigência"])
def test_accented_body_found_by_either_spelling(vault, query):
    (vault / "Legislação" / "Norma Alfa.md").write_text(
        "---\ntype: legislacao\n---\n\nA legislação mudou. Vigência a partir de 2026-01-01.\n",
        encoding="utf-8")
    assert _paths(query) == ["Legislação/Norma Alfa.md"]


def test_accented_file_name_found_by_unaccented_query_and_back(vault):
    (vault / "Legislação" / "Revisão de Honorários.md").write_text(
        "---\ntype: decisao\n---\n\ncorpo sem a palavra\n", encoding="utf-8")
    assert _paths("revisao honorarios") == ["Legislação/Revisão de Honorários.md"]
    (vault / "Legislação" / "Revisao Simples.md").write_text(
        "---\ntype: decisao\n---\n\ncorpo\n", encoding="utf-8")
    assert "Legislação/Revisao Simples.md" in _paths("Revisão")


def test_snippet_still_points_at_the_match(vault):
    body = "x " * 300 + "A Vigência começa em janeiro. " + "y " * 300
    (vault / "Legislação" / "Longa.md").write_text(f"---\ntype: n\n---\n\n{body}\n", encoding="utf-8")
    snippet = vault_ops.search("vigencia", semantic=False)[0]["snippet"]
    assert "Vigência" in snippet


def test_cjk_search_unchanged(vault):
    (vault / "知識.md").write_text("---\ntype: n\n---\n\n知識管理の系統\n", encoding="utf-8")
    assert _paths("知識管理") == ["知識.md"]

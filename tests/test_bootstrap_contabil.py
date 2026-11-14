"""The pt-BR `contabil` preset: folders, templates, manual, and safety on an
existing office vault (files the office wrote must survive bootstrap)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from _bash import BASH

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / "hooks/validate-ai-first.sh"
CONTENT_FOLDERS = ["Clientes", "Processos", "Legislação", "Decisões", "Fontes"]
SYSTEM_FOLDERS = ["Daily", "Boards", "Templates", "_trash"]
BANNED = "".join(chr(c) for c in (0x2014, 0x2013, 0x201C, 0x201D, 0x2018, 0x2019, 0x2026, 0x2265, 0x2264, 0x2260, 0xA0))


def _boot(vault: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/bootstrap_vault.py", "--path", str(vault),
         "--name", "Maria Teste", "--preset", "contabil", *extra],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, PYTHONIOENCODING="utf-8"),
    )


def _fill(text: str) -> str:
    """What Templater does: replace the placeholders with plain values."""
    text = re.sub(r"<% tp\.date\.now\([^)]*\) %>", "2026-11-14", text)
    return text.replace("<% tp.file.title %>", "Exemplo")


@pytest.fixture()
def vault(tmp_path):
    v = tmp_path / "cofre"
    r = _boot(v)
    assert r.returncode == 0, r.stderr
    return v


def test_content_folders_are_portuguese_and_system_folders_keep_their_names(vault):
    names = {p.name for p in vault.iterdir() if p.is_dir()}
    for f in CONTENT_FOLDERS + SYSTEM_FOLDERS:
        assert f in names
    assert "Modelos" not in names and "Clients" not in names


def test_templates_exist_and_carry_the_machine_contract(vault):
    templates = sorted((vault / "Templates").glob("*.md"))
    assert {t.stem for t in templates} == {
        "Cliente", "Processo", "Mudança de lei", "Decisão", "Fonte"}
    for t in templates:
        text = t.read_text(encoding="utf-8")
        assert "ai-first: true" in text and "## For future agent" in text
        for key in ("date:", "type:", "tags:"):
            assert re.search(rf"^{key}", text, re.M), (t.name, key)


def test_generated_text_has_no_banned_characters(vault):
    for f in vault.rglob("*.md"):
        text = f.read_text(encoding="utf-8")
        assert not any(c in text for c in BANNED), f.name


def test_manual_declares_language_folder_map_and_secrets_rule(vault):
    m = (vault / "_CLAUDE.md").read_text(encoding="utf-8")
    assert "português do Brasil" in m
    assert "AGENTS.md" in m and "CLAUDE.md" in m
    for f in CONTENT_FOLDERS:
        assert f"`{f}/`" in m
    assert "`Templates`" in m and "de propósito" in m
    for secret in ("senhas", "tokens", ".pfx"):
        assert secret in m
    home = (vault / "Home.md").read_text(encoding="utf-8")
    assert "Para revisar esta semana" in home
    assert "[[Clientes]]" not in home


def test_bootstrap_on_existing_office_vault_keeps_their_files(tmp_path):
    v = tmp_path / "escritorio"
    v.mkdir()
    mine = {
        "AGENTS.md": "# Regras do escritório\nResponda sempre em português.\n",
        "CLAUDE.md": "@AGENTS.md\n",
        "Home.md": "# Painel do escritório\n- [[Clientes/Alfa]]\n",
        "Clientes/Alfa.md": "# Alfa\nCliente antigo.\n",
        "Processos/Fechamento.md": "# Fechamento\n1. Conferir.\n",
        "Legislação/Norma X.md": "# Norma X\n",
        "Decisões/D1.md": "# D1\n",
        "Fontes/F1.md": "# F1\n",
        "Modelos/Modelo antigo.md": "# modelo\n",
    }
    for rel, body in mine.items():
        p = v / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(body.encode("utf-8"))
    before = {rel: (v / rel).read_bytes() for rel in mine}

    r = _boot(v)
    assert r.returncode == 0, r.stderr
    for rel, data in before.items():
        assert (v / rel).read_bytes() == data, f"{rel} was changed by bootstrap"
    assert "Modelos" in {p.name for p in v.iterdir()}
    manual = (v / "_CLAUDE.md").read_text(encoding="utf-8")
    assert "AGENTS.md" in manual and "Nunca os sobrescreva" in manual


def test_contabil_is_personal_mode_only(tmp_path):
    r = _boot(tmp_path / "x", "--mode", "assistant", "--subject", "Fulano")
    assert r.returncode != 0


def test_wiki_style_builds_too(tmp_path):
    r = _boot(tmp_path / "w", "--style", "wiki")
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "w" / "templates" / "Cliente.md").exists()


@pytest.mark.parametrize("template", ["Cliente", "Processo", "Mudança de lei", "Decisão", "Fonte"])
def test_filled_templates_pass_the_validator(vault, template):
    src = (vault / "Templates" / f"{template}.md").read_text(encoding="utf-8")
    folder = {"Cliente": "Clientes", "Processo": "Processos", "Mudança de lei": "Legislação",
              "Decisão": "Decisões", "Fonte": "Fontes"}[template]
    note = vault / folder / "Exemplo.md"
    note.write_text(_fill(src), encoding="utf-8")
    res = subprocess.run(
        [BASH, str(HOOK)],
        input=json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(note)}}),
        env=dict(os.environ, OBSIDIAN_VAULT_PATH=str(vault)),
        capture_output=True, text=True, encoding="utf-8",
    )
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip() == "", res.stdout


def test_filled_sample_note_in_portuguese_passes_the_validator(vault):
    note = vault / "Clientes" / "Padaria Alfa.md"
    note.write_text(
        "---\ndate: 2026-11-14\ntype: cliente\ntags:\n  - cliente\nai-first: true\n"
        "cliente: Padaria Alfa\nconfianca: fato\n---\n\n# Padaria Alfa\n\n"
        "## For future agent\n\nFicha da Padaria Alfa. Consulte antes de qualquer trabalho.\n\n"
        "## Como atendemos\n\nRegime Simples Nacional. Fechamento até o dia 10 (fato, "
        "combinado interno de 2026-11-14).\n",
        encoding="utf-8",
    )
    res = subprocess.run(
        [BASH, str(HOOK)],
        input=json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(note)}}),
        env=dict(os.environ, OBSIDIAN_VAULT_PATH=str(vault)),
        capture_output=True, text=True, encoding="utf-8",
    )
    assert res.stdout.strip() == "", res.stdout

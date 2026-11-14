"""setup.sh edits settings.json in Python, so a machine without jq can install."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from _bash import BASH

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import setup_settings as ss  # noqa: E402

ARGS = ("/vault", "/h/obsidian-bg-agent.sh", "/h/load_vault_context.sh",
        "/h/obsidian-recall.sh", "/h/obsidian-save-reminder.sh")


def _cmds(settings, event):
    return [h["command"] for g in settings["hooks"].get(event, []) for h in g["hooks"]]


def test_fresh_settings_get_env_and_all_four_hooks():
    s, lines = ss.apply({}, *ARGS)
    assert s["env"]["OBSIDIAN_VAULT_PATH"] == "/vault"
    assert _cmds(s, "PostCompact") == ["/h/obsidian-bg-agent.sh"]
    assert s["hooks"]["PostCompact"][0]["hooks"][0]["async"] is True
    assert _cmds(s, "SessionStart") == ["/h/load_vault_context.sh"]
    assert _cmds(s, "UserPromptSubmit") == ["/h/obsidian-recall.sh"]
    assert _cmds(s, "Stop") == ["/h/obsidian-save-reminder.sh"]
    assert "matcher" not in s["hooks"]["Stop"][0]  # Stop takes no matcher
    assert any("registered" in line for line in lines)


def test_second_run_changes_nothing():
    once, _ = ss.apply({}, *ARGS)
    snapshot = json.dumps(once, sort_keys=True)
    twice, lines = ss.apply(once, *ARGS)
    assert json.dumps(twice, sort_keys=True) == snapshot
    assert sum("skipping" in line for line in lines) == 4  # four hooks all already there


def test_old_python3_session_hook_is_rewritten_not_duplicated():
    old = {"hooks": {"SessionStart": [{"matcher": "", "hooks": [
        {"type": "command", "command": "python3 /old/hooks/load_vault_context.py"}]}]}}
    s, lines = ss.apply(old, *ARGS)
    assert _cmds(s, "SessionStart") == ["/h/load_vault_context.sh"]
    assert "SessionStart hook updated to the interpreter-resolving wrapper" in lines


def test_unrelated_settings_and_hooks_survive_and_vault_path_is_replaced():
    s0 = {"model": "x", "env": {"OTHER": "1", "OBSIDIAN_VAULT_PATH": "/old"},
          "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "/other/peon.sh"}]}]}}
    s, _ = ss.apply(s0, *ARGS)
    assert s["model"] == "x" and s["env"] == {"OTHER": "1", "OBSIDIAN_VAULT_PATH": "/vault"}
    assert _cmds(s, "Stop") == ["/other/peon.sh", "/h/obsidian-save-reminder.sh"]


def _run(tmp_path, settings_text=None, path_override=None):
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    if settings_text is not None:
        (home / ".claude" / "settings.json").write_text(settings_text, encoding="utf-8")
    vault = tmp_path / "meu cofre"
    vault.mkdir()
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home))
    env.pop("OBSIDIAN_ENV_FILE", None)
    if path_override is not None:
        env["PATH"] = path_override
    r = subprocess.run([BASH, str(REPO_ROOT / "scripts/setup.sh"), str(vault)],
                       input="N\n", env=env, capture_output=True, text=True, timeout=120)
    return r, home / ".claude" / "settings.json", vault


def test_setup_sh_works_without_jq_and_is_idempotent(tmp_path):
    # A PATH that has bash tools and Python but no jq: a dir of symlinks to what the script needs.
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for tool in ("bash", "sh", "dirname", "cat", "mkdir", "chmod", "mv", "rm", "ln", "awk",
                 "sed", "grep", "uname", "tr", "head", "env", "id", "basename", "cygpath"):
        found = shutil.which(tool)
        if found:
            (bindir / tool).symlink_to(found)
    (bindir / "python3").symlink_to(sys.executable)
    r, settings_path, vault = _run(tmp_path, path_override=str(bindir))
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    assert shutil.which("jq", path=str(bindir)) is None
    s = json.loads(settings_path.read_text(encoding="utf-8"))
    assert s["env"]["OBSIDIAN_VAULT_PATH"] == str(vault)
    for event in ("SessionStart", "UserPromptSubmit", "Stop", "PostCompact"):
        assert s["hooks"][event], event
    first = settings_path.read_text(encoding="utf-8")
    r2, _, _ = _run_again(tmp_path, settings_path, bindir)
    assert r2.returncode == 0
    assert settings_path.read_text(encoding="utf-8") == first


def _run_again(tmp_path, settings_path, bindir):
    home = settings_path.parent.parent
    vault = next(p for p in tmp_path.iterdir() if p.name == "meu cofre")
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), PATH=str(bindir))
    env.pop("OBSIDIAN_ENV_FILE", None)
    r = subprocess.run([BASH, str(REPO_ROOT / "scripts/setup.sh"), str(vault)],
                       input="N\n", env=env, capture_output=True, text=True, timeout=120)
    return r, settings_path, vault


def test_setup_sh_refuses_invalid_json_and_leaves_it_alone(tmp_path):
    r, settings_path, _ = _run(tmp_path, settings_text="{ not json")
    assert r.returncode != 0
    assert "invalid JSON" in (r.stdout + r.stderr)
    assert settings_path.read_text(encoding="utf-8") == "{ not json"


def test_setup_sh_no_longer_mentions_jq_as_a_requirement():
    text = (REPO_ROOT / "scripts/setup.sh").read_text(encoding="utf-8")
    assert "command -v jq" not in text and "| jq" not in text and "jq -" not in text


@pytest.mark.parametrize("name", ["setup_settings.py"])
def test_script_has_a_cli(name):
    r = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / name), "--help"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "--settings" in r.stdout


# ── the write validator without jq ───────────────────────────────────────────

def _no_jq_path(tmp_path):
    bindir = tmp_path / "nojq"
    bindir.mkdir()
    for tool in ("bash", "sh", "dirname", "cat", "mkdir", "chmod", "mv", "rm", "awk", "sed",
                 "grep", "uname", "tr", "head", "env", "basename", "od", "mktemp", "tail",
                 "cygpath"):
        found = shutil.which(tool)
        if found:
            (bindir / tool).symlink_to(found)
    (bindir / "python3").symlink_to(sys.executable)
    assert shutil.which("jq", path=str(bindir)) is None
    return str(bindir)


def test_validator_still_warns_when_jq_is_missing(tmp_path):
    vault = tmp_path / "v"
    (vault / "Clientes").mkdir(parents=True)
    note = vault / "Clientes" / "A.md"
    note.write_text("# sem frontmatter\n", encoding="utf-8")
    payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(note)}})
    env = dict(os.environ, PATH=_no_jq_path(tmp_path), OBSIDIAN_VAULT_PATH=str(vault))
    r = subprocess.run([BASH, str(REPO_ROOT / "hooks/validate-ai-first.sh")], input=payload,
                       env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert "no frontmatter" in out["systemMessage"]
    assert out["hookSpecificOutput"]["hookEventName"] == "PostToolUse"


def test_validator_is_quiet_on_a_good_note_without_jq(tmp_path):
    vault = tmp_path / "v"
    (vault / "Clientes").mkdir(parents=True)
    note = vault / "Clientes" / "B.md"
    note.write_text("---\ndate: 2026-11-14\ntype: cliente\ntags:\n  - cliente\nai-first: true\n"
                    "---\n\n# B\n\n## For future agent\n\nFicha.\n", encoding="utf-8")
    payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(note)}})
    env = dict(os.environ, PATH=_no_jq_path(tmp_path), OBSIDIAN_VAULT_PATH=str(vault))
    r = subprocess.run([BASH, str(REPO_ROOT / "hooks/validate-ai-first.sh")], input=payload,
                       env=env, capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.strip() == "", (r.stdout, r.stderr)

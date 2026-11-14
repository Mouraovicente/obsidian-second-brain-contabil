"""Automatic memory without ai-memory: recall on by default and the Stop reminder."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from _bash import BASH

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOKS = REPO_ROOT / "hooks"
MCP_SAVE = "mcp__plugin_obsidian-second-brain_vault__obsidian_save_note"


# ── hooks.json shape ─────────────────────────────────────────────────────────

def test_hooks_json_registers_recall_and_reminder_through_wrappers():
    hooks = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    assert set(hooks) == {"SessionStart", "UserPromptSubmit", "PostToolUse", "Stop", "PostCompact"}
    ups = hooks["UserPromptSubmit"][0]["hooks"][0]["command"]
    stop = hooks["Stop"][0]["hooks"][0]["command"]
    assert "obsidian-recall.sh" in ups and "obsidian-save-reminder.sh" in stop
    for cmd in (ups, stop):
        assert not cmd.strip().startswith("python3"), cmd
    # Stop has no matcher in Claude Code; do not pretend it does.
    assert "matcher" not in hooks["Stop"][0]


@pytest.mark.parametrize("name", ["obsidian-recall.sh", "obsidian-save-reminder.sh"])
def test_wrappers_are_executable_and_parse(name):
    assert os.access(HOOKS / name, os.X_OK)
    r = subprocess.run([BASH, "-n", str(HOOKS / name)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


# ── recall: default on, opt out with 0 ───────────────────────────────────────

@pytest.fixture()
def vault(tmp_path):
    v = tmp_path / "cofre"
    v.mkdir()
    (v / "Padaria Alfa.md").write_text(
        "---\ntype: cliente\n---\n# Padaria Alfa\n\nFechamento mensal da padaria até o dia 10.\n",
        encoding="utf-8")
    return v


def _recall(vault, prompt, **env):
    e = {k: v for k, v in os.environ.items() if not k.startswith("OBSIDIAN_")}
    e["OBSIDIAN_VAULT_PATH"] = str(vault)
    e.update(env)
    return subprocess.run([BASH, str(HOOKS / "obsidian-recall.sh")],
                          input=json.dumps({"prompt": prompt}), env=e,
                          capture_output=True, text=True)


def test_recall_is_on_by_default_through_the_wrapper(vault):
    r = _recall(vault, "qual o prazo de fechamento mensal da padaria?")
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "UserPromptSubmit"
    assert "[[Padaria Alfa]]" in out["additionalContext"]


def test_recall_opt_out_and_abstention(vault):
    off = _recall(vault, "qual o prazo de fechamento mensal da padaria?",
                  OBSIDIAN_RECALL_ENABLED="0")
    assert off.returncode == 0 and off.stdout == ""
    weak = _recall(vault, "explique cromodinamica quantica em rede")
    assert weak.returncode == 0 and weak.stdout == ""


def test_recall_is_silent_without_a_vault(tmp_path):
    e = {k: v for k, v in os.environ.items() if not k.startswith("OBSIDIAN_")}
    r = subprocess.run([BASH, str(HOOKS / "obsidian-recall.sh")],
                       input=json.dumps({"prompt": "qualquer pergunta longa o bastante"}),
                       env=e, capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout == ""


def test_recall_never_injects_the_manual(tmp_path):
    v = tmp_path / "v"
    v.mkdir()
    (v / "_CLAUDE.md").write_text("# Manual\n\nfechamento mensal regras\n", encoding="utf-8")
    r = _recall(v, "fechamento mensal regras do escritorio")
    assert r.stdout == ""


# ── save reminder ────────────────────────────────────────────────────────────

def _transcript(path: Path, tool_uses: list[tuple[str, dict]]) -> Path:
    lines = [json.dumps({"type": "user", "message": {"role": "user", "content": "oi"}})]
    for name, args in tool_uses:
        lines.append(json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "ok"},
            {"type": "tool_use", "id": "t1", "name": name, "input": args}]}}))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


class Reminder:
    def __init__(self, tmp_path, vault):
        self.vault = vault
        self.tmp = tmp_path
        self.session = f"sess-{tmp_path.name}"
        self.transcript = tmp_path / "t.jsonl"
        _transcript(self.transcript, [])

    def stop(self, *, active=False, session=None, **env):
        e = {k: v for k, v in os.environ.items() if not k.startswith("OBSIDIAN_")}
        e.update(OBSIDIAN_VAULT_PATH=str(self.vault), TMPDIR=str(self.tmp / "tmp"),
                 TEMP=str(self.tmp / "tmp"), TMP=str(self.tmp / "tmp"))
        (self.tmp / "tmp").mkdir(exist_ok=True)
        e.update(env)
        payload = {"session_id": session or self.session, "transcript_path": str(self.transcript),
                   "cwd": str(self.vault), "stop_hook_active": active,
                   "last_assistant_message": "pronto"}
        r = subprocess.run([BASH, str(HOOKS / "obsidian-save-reminder.sh")],
                           input=json.dumps(payload), env=e, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        return r.stdout

    def fired(self, out: str) -> bool:
        if not out.strip():
            return False
        o = json.loads(out)["hookSpecificOutput"]
        assert o["hookEventName"] == "Stop"
        assert "/obsidian-save" in o["additionalContext"]
        return True


@pytest.fixture()
def rem(tmp_path, vault):
    return Reminder(tmp_path, vault)


def test_reminder_fires_after_n_turns_without_a_write_then_resets(rem):
    env = {"OBSIDIAN_SAVE_REMINDER_TURNS": "3"}
    assert [rem.fired(rem.stop(**env)) for _ in range(3)] == [False, False, True]
    # counter reset: the next window starts from zero
    assert [rem.fired(rem.stop(**env)) for _ in range(3)] == [False, False, True]


def test_default_threshold_is_six(rem):
    assert [rem.fired(rem.stop()) for _ in range(6)] == [False] * 5 + [True]


def test_a_vault_write_restarts_the_window_write_tool(rem):
    env = {"OBSIDIAN_SAVE_REMINDER_TURNS": "3"}
    rem.stop(**env)
    rem.stop(**env)
    _transcript(rem.transcript, [("Write", {"file_path": str(rem.vault / "Clientes" / "A.md")})])
    assert rem.fired(rem.stop(**env)) is False  # third turn, but a write happened
    assert [rem.fired(rem.stop(**env)) for _ in range(3)] == [False, False, True]


def test_a_vault_write_restarts_the_window_mcp_save(rem):
    env = {"OBSIDIAN_SAVE_REMINDER_TURNS": "2"}
    rem.stop(**env)
    _transcript(rem.transcript, [(MCP_SAVE, {"path": "Clientes/A.md", "content": "x"})])
    assert rem.fired(rem.stop(**env)) is False


def test_a_write_outside_the_vault_does_not_count(rem, tmp_path):
    env = {"OBSIDIAN_SAVE_REMINDER_TURNS": "2"}
    rem.stop(**env)
    other = tmp_path / "outro" / "x.md"
    # a sibling whose name merely starts with the vault name must not match either
    sibling = Path(str(rem.vault) + "-copia") / "x.md"
    _transcript(rem.transcript, [("Write", {"file_path": str(other)}),
                                 ("Edit", {"file_path": str(sibling)})])
    assert rem.fired(rem.stop(**env)) is True


def test_stop_hook_active_never_acts_and_does_not_count(rem):
    env = {"OBSIDIAN_SAVE_REMINDER_TURNS": "2"}
    rem.stop(**env)
    assert rem.stop(active=True, **env) == ""
    assert rem.fired(rem.stop(**env)) is True  # the active stop was not counted


def test_gates_are_silent(rem, tmp_path):
    env = {"OBSIDIAN_SAVE_REMINDER_TURNS": "1"}
    assert rem.stop(OBSIDIAN_SAVE_REMINDER="0", **env) == ""
    assert rem.stop(OBSIDIAN_VAULT_PATH=str(tmp_path / "nao-existe"), **env) == ""
    assert rem.fired(rem.stop(**env)) is True


def test_sessions_are_counted_separately(rem):
    env = {"OBSIDIAN_SAVE_REMINDER_TURNS": "2"}
    rem.stop(session="a", **env)
    assert rem.fired(rem.stop(session="b", **env)) is False
    assert rem.fired(rem.stop(session="a", **env)) is True


def test_corrupt_state_and_missing_transcript_are_tolerated(rem, tmp_path):
    env = {"OBSIDIAN_SAVE_REMINDER_TURNS": "2"}
    rem.stop(**env)
    state = next((tmp_path / "tmp").rglob("*.json"))
    state.write_text("{not json", encoding="utf-8")
    rem.transcript.unlink()
    assert rem.stop(**env) == ""          # restarted from zero, no crash
    assert rem.fired(rem.stop(**env)) is True


def test_bad_stdin_is_silent(vault):
    e = dict(os.environ, OBSIDIAN_VAULT_PATH=str(vault))
    r = subprocess.run([sys.executable, str(HOOKS / "obsidian-save-reminder.py")],
                       input="not json", env=e, capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout == ""

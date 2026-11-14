#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Eugeniu Ghelbur and contributors
# SPDX-License-Identifier: MIT
# Author: Eugeniu Ghelbur (AI Automation Engineer, AI Tooling Engineer, AI Educator), https://github.com/eugeniughelbur/obsidian-second-brain
# Questions or consulting: e.ghelbur@gmail.com | https://www.linkedin.com/in/eugeniu-ghelbur/ | More: https://theaioperator.io | https://x.com/eugeniu_ghelbur
"""Edit ~/.claude/settings.json for scripts/setup.sh without jq.

setup.sh used jq for these edits, and jq is not on a stock Windows machine.
This does the same work in Python, which the toolkit already needs:

  - env.OBSIDIAN_VAULT_PATH = <vault>
  - PostCompact: the background-agent hook (inert until armed), added once
  - SessionStart: the context hook; an older entry (a pre-#269 `python3 ...py`)
    is rewritten in place, never duplicated
  - UserPromptSubmit and Stop: the recall and save-reminder hooks, added once
    so a classic (non-plugin) install gets the same automatic memory the plugin
    registers through hooks/hooks.json

Idempotent, and it touches nothing else in the file. Exit 1 with a message when
the file is not valid JSON, so a hand-edited settings.json is never clobbered.

Usage: setup_settings.py --settings FILE --vault DIR --postcompact CMD
                         --session CMD --recall CMD --stop CMD
"""
from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path


def _commands(settings: dict, event: str) -> list[str]:
    return [
        h.get("command", "")
        for group in settings.get("hooks", {}).get(event, [])
        for h in group.get("hooks", [])
    ]


def _add(settings: dict, event: str, group: dict) -> None:
    settings.setdefault("hooks", {}).setdefault(event, []).append(group)


def apply(settings: dict, vault: str, postcompact: str, session: str,
          recall: str, stop: str) -> tuple[dict, list[str]]:
    """Pure: returns the new settings and one status line per step."""
    out: list[str] = []
    env = settings.get("env")
    if not isinstance(env, dict):
        env = settings["env"] = {}
    env["OBSIDIAN_VAULT_PATH"] = vault
    out.append("OBSIDIAN_VAULT_PATH set")

    if any(postcompact in c for c in _commands(settings, "PostCompact")):
        out.append("PostCompact hook already configured - skipping")
    else:
        _add(settings, "PostCompact", {"matcher": "", "hooks": [{
            "type": "command", "command": postcompact, "timeout": 10, "async": True}]})
        out.append("PostCompact hook registered (inert by default)")

    # Matched on the script name: an install made before #269 registered
    # `python3 <...>/load_vault_context.py`, which does nothing on Windows.
    found = [c for c in _commands(settings, "SessionStart") if "load_vault_context" in c]
    if not found:
        _add(settings, "SessionStart", {"matcher": "", "hooks": [{
            "type": "command", "command": session}]})
        out.append("SessionStart hook wired (injects _CLAUDE.md once per session)")
    elif all(c == session for c in found):
        out.append("SessionStart hook already configured - skipping")
    else:
        for group in settings["hooks"]["SessionStart"]:
            for h in group.get("hooks", []):
                if "load_vault_context" in h.get("command", ""):
                    h["command"] = session
        out.append("SessionStart hook updated to the interpreter-resolving wrapper")

    for event, cmd, script, extra in (
        ("UserPromptSubmit", recall, "obsidian-recall", {"timeout": 15}),
        ("Stop", stop, "obsidian-save-reminder", {"timeout": 10}),
    ):
        if any(script in c for c in _commands(settings, event)):
            out.append(f"{event} hook already configured - skipping")
        else:
            _add(settings, event, {"hooks": [{"type": "command", "command": cmd, **extra}]})
            out.append(f"{event} hook registered ({script})")
    return settings, out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("settings", "vault", "postcompact", "session", "recall", "stop"):
        ap.add_argument(f"--{name}", required=True)
    a = ap.parse_args(argv)

    path = Path(a.settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        try:
            settings = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            settings = None
        if not isinstance(settings, dict):
            print(f"Error: {path} contains invalid JSON. Fix it first.", file=sys.stderr)
            return 1
    else:
        settings = {}
        print(f"   Created {path}")

    # shlex.quote leaves an ordinary path exactly as written and protects one with
    # a space, which the shell that runs the hook would otherwise split.
    q = shlex.quote
    settings, lines = apply(settings, a.vault, q(a.postcompact), q(a.session),
                            q(a.recall), q(a.stop))
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    for line in lines:
        print(f"   {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

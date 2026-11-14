#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Eugeniu Ghelbur and contributors
# SPDX-License-Identifier: MIT
# Author: Eugeniu Ghelbur (AI Automation Engineer, AI Tooling Engineer, AI Educator), https://github.com/eugeniughelbur/obsidian-second-brain
# Questions or consulting: e.ghelbur@gmail.com | https://www.linkedin.com/in/eugeniu-ghelbur/ | More: https://theaioperator.io | https://x.com/eugeniu_ghelbur
"""Save reminder - Stop hook.

Without another memory tool, nothing makes the agent save what a long
conversation produced. This hook counts finished turns (Stop events) per
session. When N turns (default 6, OBSIDIAN_SAVE_REMINDER_TURNS) have passed
since the session started, the last reminder, or the last vault write, it asks
Claude once to save anything durable with the /obsidian-save procedure.

Claude Code semantics (hooks reference, Stop event): the input carries
session_id, transcript_path, stop_hook_active and last_assistant_message; the
output {"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": ...}}
makes Claude continue once, shown as non-error "Stop hook feedback". Claude Code
caps consecutive continuations, and this hook never acts while stop_hook_active
is true, so it cannot loop.

Gates (all fail closed, exit 0, no output): OBSIDIAN_VAULT_PATH unset or not a
directory; OBSIDIAN_SAVE_REMINDER=0; stop_hook_active; unparseable input.

Vault-write detection scans the session transcript instead of having the
PostToolUse validator leave a marker. The validator needs jq and only matches
Write/Edit tools, so it would miss the MCP save tools and be blind on a machine
without jq; the transcript is the single place that records every write, and
reading it needs nothing installed. The scan is incremental: the state keeps
how many transcript lines were already read.

State: one small JSON file per session under the OS temp dir. Missing or corrupt
state restarts the count. No network, nothing written to the vault.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

DEFAULT_TURNS = 6

REMINDER = (
    "Lembrete do cofre: esta conversa já teve vários turnos sem nada gravado no cofre. "
    "Se ela produziu algo que vale guardar (uma decisão, um combinado com cliente, "
    "um passo de processo, uma mudança de norma com fonte), siga o procedimento do "
    "/obsidian-save e diga ao usuário o que foi salvo e onde. "
    "Se não há nada durável, termine sem salvar e sem comentar este lembrete."
)

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "create_file"}
# Plugin install: mcp__plugin_<plugin>_<server>__obsidian_save_note; manual MCP
# install: mcp__<server>__obsidian_save_note. Matching on the tool suffix covers both.
MCP_WRITE_RE = re.compile(
    r"^mcp__.+__obsidian_(save_note|capture|update_note|replace_text|move_note)$"
)


def _norm(p: str) -> str:
    """One comparison form for a path: forward slashes, MSYS /c/x or
    /cygdrive/c/x turned into c:/x, lowercase on Windows (case-insensitive disk)."""
    p = p.replace("\\", "/")
    m = re.match(r"^/(?:cygdrive/)?([A-Za-z])(/.*)?$", p)
    if m and os.name == "nt":
        p = f"{m.group(1)}:{m.group(2) or '/'}"
    p = p.rstrip("/")
    return p.lower() if os.name == "nt" else p


def _turns_threshold() -> int:
    try:
        return max(1, int(os.environ.get("OBSIDIAN_SAVE_REMINDER_TURNS", DEFAULT_TURNS)))
    except ValueError:
        return DEFAULT_TURNS


def _state_path(session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id)[:80] or "unknown"
    return Path(tempfile.gettempdir()) / "obsidian-second-brain-save-reminder" / f"{safe}.json"


def _load_state(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {"turns": max(0, int(data["turns"])), "offset": max(0, int(data["offset"]))}
    except (OSError, ValueError, KeyError, TypeError):
        return {"turns": 0, "offset": 0}


def _save_state(path: Path, state: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass  # the reminder is a convenience; losing state only delays it


def scan_transcript(transcript: str, vault: str, offset: int) -> tuple[bool, int]:
    """(vault write seen after line `offset`, total line count)."""
    vault_key = _norm(vault)
    wrote = False
    total = 0
    try:
        with Path(transcript).open(encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                total = i + 1
                if i < offset or wrote:
                    continue
                try:
                    content = (json.loads(line).get("message") or {}).get("content")
                except (ValueError, AttributeError):
                    continue
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    name = str(block.get("name", ""))
                    args = block.get("input") if isinstance(block.get("input"), dict) else {}
                    if MCP_WRITE_RE.match(name):
                        wrote = True
                    elif name in WRITE_TOOLS:
                        target = args.get("file_path") or args.get("filePath") or ""
                        if target and _norm(str(target)).startswith(vault_key + "/"):
                            wrote = True
    except OSError:
        return False, offset
    return wrote, total


def main() -> int:
    vault = os.environ.get("OBSIDIAN_VAULT_PATH", "").strip()
    if not vault or not Path(vault).is_dir():
        return 0
    if os.environ.get("OBSIDIAN_SAVE_REMINDER", "").strip() == "0":
        return 0
    try:
        payload = json.loads(sys.stdin.read())
    except ValueError:
        return 0
    if not isinstance(payload, dict) or payload.get("stop_hook_active"):
        return 0

    session_id = str(payload.get("session_id") or "")
    if not session_id:
        return 0
    path = _state_path(session_id)
    state = _load_state(path)
    state["turns"] += 1

    transcript = str(payload.get("transcript_path") or "")
    if transcript:
        wrote, total = scan_transcript(transcript, vault, state["offset"])
        state["offset"] = total
        if wrote:
            state["turns"] = 0  # something was saved: the window restarts

    if state["turns"] >= _turns_threshold():
        state["turns"] = 0
        _save_state(path, state)
        print(json.dumps({
            "hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": REMINDER}
        }, ensure_ascii=False))
        return 0
    _save_state(path, state)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - fail closed: a reminder must never break a stop
        sys.exit(0)

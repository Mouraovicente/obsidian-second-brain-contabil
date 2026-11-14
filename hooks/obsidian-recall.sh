#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Eugeniu Ghelbur and contributors
# SPDX-License-Identifier: MIT
# Written for the obsidian-second-brain-contabil fork (https://github.com/Mouraovicente/obsidian-second-brain-contabil), not by the original author. Report issues to the fork.
# =============================================================================
# obsidian-recall.sh - UserPromptSubmit hook entry point (vault recall)
# =============================================================================
# Wrapper that finds a Python that actually runs (the bare name python3 is the
# Microsoft Store stub on Windows, see scripts/python-interpreter.sh) and hands
# it the hook payload on stdin. The interpreter helper is sourced from
# scripts/, not copied, so there is one definition. When no Python exists the
# hook says so on stderr and exits 0: this hook is a convenience and must never
# block a prompt or a stop.
# =============================================================================

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HOOK_DIR/../scripts/python-interpreter.sh" 2>/dev/null || exit 0

# Nothing to do without a vault: stay silent and cheap.
[[ -z "${OBSIDIAN_VAULT_PATH:-}" ]] && exit 0

PYTHON=$(osb_python) || {
  printf 'obsidian-second-brain: no working Python found, so obsidian-recall.sh did nothing.\n' >&2
  exit 0
}

# Unquoted: PYTHON may be several words ("py -3", "uv run --no-project python").
exec $PYTHON "$HOOK_DIR/obsidian-recall.py"

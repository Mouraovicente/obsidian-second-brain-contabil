#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Eugeniu Ghelbur and contributors
# SPDX-License-Identifier: MIT
# Author: Eugeniu Ghelbur (AI Automation Engineer, AI Tooling Engineer, AI Educator), https://github.com/eugeniughelbur/obsidian-second-brain
# Questions or consulting: e.ghelbur@gmail.com | https://www.linkedin.com/in/eugeniu-ghelbur/ | More: https://theaioperator.io | https://x.com/eugeniu_ghelbur
# setup.sh - obsidian-second-brain one-command installer
#
# Usage:
#   bash ~/.claude/skills/obsidian-second-brain/scripts/setup.sh "/path/to/your/vault"
#
# What it does:
#   1. Validates the vault path
#   2. Adds OBSIDIAN_VAULT_PATH to ~/.claude/settings.json (Python, no jq)
#   3. Wires the SessionStart, UserPromptSubmit (recall), Stop (save reminder)
#      and PostCompact (inert) hooks
#   4. Makes the hook scripts executable
#   5. Registers slash commands in ~/.claude/commands/
#   6. Configures the MCP server for Claude Code (optional)

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Home for config and Claude Code state (OSB_HOME, OSB_WIN): USERPROFILE on
# Windows shells, HOME elsewhere. See scripts/platform-home.sh.
. "$SKILL_DIR/scripts/platform-home.sh"
osb_platform_home
SETTINGS="$OSB_HOME/.claude/settings.json"
HOOK_SCRIPT="$SKILL_DIR/hooks/obsidian-bg-agent.sh"
# The .sh wrapper, not the .py: it resolves an interpreter that actually runs
# before handing over, which the bare `python3` name does not do on Windows (#269).
SESSION_HOOK="$SKILL_DIR/hooks/load_vault_context.sh"
RECALL_HOOK="$SKILL_DIR/hooks/obsidian-recall.sh"
STOP_HOOK="$SKILL_DIR/hooks/obsidian-save-reminder.sh"
osb_env_file
ENV_FILE="$OSB_ENV_FILE"

# ── helpers ──────────────────────────────────────────────────────────────────

green()  { printf '\033[0;32m%s\033[0m\n' "$1"; }
yellow() { printf '\033[0;33m%s\033[0m\n' "$1"; }
red()    { printf '\033[0;31m%s\033[0m\n' "$1"; }
step()   { printf '\n\033[1m%s\033[0m\n' "$1"; }

# Python edits settings.json (no jq needed, which matters on Windows). The
# resolver runs each candidate, because the bare name python3 is the Microsoft
# Store stub there (#269).
. "$SKILL_DIR/scripts/python-interpreter.sh"
PYTHON=$(osb_python) || {
  red "Error: no working Python found (tried python3, python, py -3, uv run)."
  echo "Install Python from python.org or uv from astral.sh, then run this again."
  exit 1
}

# ── vault path ───────────────────────────────────────────────────────────────

VAULT="${1:-}"
if [[ -z "$VAULT" ]]; then
  red "Error: vault path required."
  echo "Usage: bash scripts/setup.sh \"/path/to/your/vault\""
  exit 1
fi

VAULT="${VAULT/#\~/$HOME}"  # expand leading ~

if [[ ! -d "$VAULT" ]]; then
  red "Error: vault directory not found: $VAULT"
  echo "No vault yet? Create one first:"
  echo "  uv run python \"$SKILL_DIR/scripts/bootstrap_vault.py\" --path \"$VAULT\" --name \"Your Name\""
  echo "then re-run this setup."
  echo "Create it first or check the path."
  exit 1
fi

echo ""
echo "obsidian-second-brain setup"
echo "==========================="
echo "Vault: $VAULT"
echo "Skill: $SKILL_DIR"
echo ""

# ── make hook executable ──────────────────────────────────────────────────────

step "1. Making hook scripts executable..."
chmod +x "$HOOK_SCRIPT"
[[ -f "$SESSION_HOOK" ]] && chmod +x "$SESSION_HOOK"
chmod +x "$RECALL_HOOK" "$STOP_HOOK"
green "   Done - $HOOK_SCRIPT"
green "   Done - $SESSION_HOOK"

# ── ensure settings.json exists ───────────────────────────────────────────────

step "2. Updating $SETTINGS..."

# Sets env.OBSIDIAN_VAULT_PATH and registers the hooks (PostCompact, SessionStart,
# UserPromptSubmit recall, Stop save reminder). Idempotent; refuses to touch a
# settings.json that is not valid JSON. PYTHON is unquoted: it may be several words.
$PYTHON "$SKILL_DIR/scripts/setup_settings.py" \
  --settings "$SETTINGS" --vault "$VAULT" \
  --postcompact "$HOOK_SCRIPT" --session "$SESSION_HOOK" \
  --recall "$RECALL_HOOK" --stop "$STOP_HOOK" || exit 1

# Wire the vault path into the config .env (if one exists) so standalone runs resolve it
if [ -f "$ENV_FILE" ]; then
  # umask 077 on the rewrite: the temp file is created fresh, so under a default
  # umask the mv silently replaced install.sh's 0600 with 0644 and exposed every
  # setting in this file to any other account on the machine. An explicit chmod is the backstop.
  ( umask 077
    VAULT="$VAULT" awk '
      /^OBSIDIAN_VAULT_PATH=/ { print "OBSIDIAN_VAULT_PATH=" ENVIRON["VAULT"]; done=1; next }
      { print }
      END { if (!done) print "OBSIDIAN_VAULT_PATH=" ENVIRON["VAULT"] }
    ' "$ENV_FILE" > "$ENV_FILE.tmp" ) && mv "$ENV_FILE.tmp" "$ENV_FILE" && chmod 600 "$ENV_FILE"
  green "   OBSIDIAN_VAULT_PATH written to research .env"
fi

echo "      The PostCompact background agent is OPT-IN - it writes unattended, so it ships off."
echo "      To enable: set OBSIDIAN_BG_AGENT_ENABLED=1 in the env section of"
echo "      ~/.claude/settings.json. See hooks/postcompact.hook.example.json."

# ── register slash commands ──────────────────────────────────────────────────

step "3. Registering slash commands in $OSB_HOME/.claude/commands/..."

COMMANDS_SRC="$SKILL_DIR/commands"
COMMANDS_DST="$OSB_HOME/.claude/commands"

if [[ ! -d "$COMMANDS_SRC" ]]; then
  yellow "   No commands/ directory in skill - skipping"
else
  mkdir -p "$COMMANDS_DST"
  linked=0
  skipped=0
  blocked=0
  for cmd in "$COMMANDS_SRC"/*.md; do
    [[ -e "$cmd" ]] || continue
    name=$(basename "$cmd")
    target="$COMMANDS_DST/$name"
    if [[ -L "$target" ]]; then
      # already a symlink - refresh it (idempotent, handles repo path changes)
      ln -snf "$cmd" "$target"
      skipped=$((skipped + 1))
    elif [[ -e "$target" ]]; then
      yellow "   Skipped $name - file already exists (not a symlink). Remove it manually if you want the skill version."
      blocked=$((blocked + 1))
    else
      ln -s "$cmd" "$target"
      linked=$((linked + 1))
    fi
  done
  green "   $linked new, $skipped refreshed, $blocked blocked"
fi

# ── optional: MCP server (Claude Code only) ───────────────────────────────────

step "4. MCP server (optional)..."
echo "   This repo ships its own MCP server (integrations/obsidian-mcp-server/)."
echo "   It is optional: in Claude Code, Claude reads/writes vault files directly"
echo "   and everything works without it. The server is mainly useful for other"
echo "   MCP clients (Claude Desktop, Cursor). It needs 'uv' on PATH."
echo ""
MCP_CMD="claude mcp add obsidian-second-brain -s user -e OBSIDIAN_VAULT_PATH=\"$VAULT\" -- uv run --no-project --with 'mcp<2' python \"$SKILL_DIR/integrations/obsidian-mcp-server/server.py\""
REPLY=n
if [[ -t 0 ]]; then
  read -r -p "   Configure the bundled MCP server? [y/N] " REPLY
fi
if [[ "$REPLY" =~ ^[Yy]$ ]]; then
  if command -v claude &>/dev/null && command -v uv &>/dev/null; then
    claude mcp add obsidian-second-brain -s user -e OBSIDIAN_VAULT_PATH="$VAULT" -- uv run --no-project --with 'mcp<2' python "$SKILL_DIR/integrations/obsidian-mcp-server/server.py"
    green "   MCP server configured"
  else
    yellow "   claude and/or uv CLI not found - skipping MCP setup"
    echo "   Run manually when ready:"
    echo "   $MCP_CMD"
  fi
else
  echo "   Skipped. Run later if you want it:"
  echo "   $MCP_CMD"
fi

# ── done ─────────────────────────────────────────────────────────────────────

echo ""
echo "==========================="
green "Setup complete."
echo ""
echo "Next step: drop a _CLAUDE.md into your vault so Claude knows how it's structured."
echo "Open Claude Code in your vault directory and run:"
echo ""
echo "   /obsidian-init"
echo ""
echo "That's it. Claude will scan your vault and generate its operating manual."
echo ""
echo "Background agent logs: \$TMPDIR/obsidian-bg-agent-\$(id -u).log"
echo "Health check:          python scripts/vault_health.py --path \"$VAULT\""
echo ""

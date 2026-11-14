# SPDX-FileCopyrightText: 2026 Eugeniu Ghelbur and contributors
# SPDX-License-Identifier: MIT
# Author: Eugeniu Ghelbur (AI Automation Engineer, AI Tooling Engineer, AI Educator), https://github.com/eugeniughelbur/obsidian-second-brain
# Questions or consulting: e.ghelbur@gmail.com | https://www.linkedin.com/in/eugeniu-ghelbur/ | More: https://theaioperator.io | https://x.com/eugeniu_ghelbur
"""Loads OBSIDIAN_VAULT_PATH and other settings from ~/.config/obsidian-second-brain/.env"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import osb_env  # noqa: E402  (depends on the sys.path insert above)

# Where the config lives is scripts/osb_env.py's question to answer, for every
# half of the toolkit (this loader, the free-mode source config, the evals, the
# SessionStart hook). Asking it here rather than spelling it out again is what
# keeps OBSIDIAN_ENV_FILE meaning the same thing in all of them.
CONFIG_DIR = osb_env.config_dir()
ENV_PATH = osb_env.env_file()

load_dotenv(ENV_PATH)


def get_required(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        raise SystemExit(
            f"\n{name} not configured.\n"
            f"Add it to {ENV_PATH}\n"
            f"Or run install.sh from the obsidian-second-brain repo to set it up.\n"
        )
    return val


def get_optional(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip() or default


def get_optional_int(name: str, default: int) -> int:
    """Integer knob from the environment. A value that is not a whole number
    (`480k`, `1e6`, `24,000`) exits with the variable named, instead of an
    `int()` traceback from somewhere inside the command."""
    raw = get_optional(name, str(default))
    try:
        return int(raw)
    except ValueError:
        raise SystemExit(
            f"\n{name}={raw!r} is not a whole number.\n"
            f"Set it to a plain integer (e.g. {name}={default}) in {ENV_PATH}, or unset it.\n"
        ) from None


VAULT_PATH = Path(get_required("OBSIDIAN_VAULT_PATH")).expanduser()

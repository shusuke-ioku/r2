"""r2 — AI-driven research environment for academic papers."""

from __future__ import annotations

import os
from pathlib import Path

__version__ = "0.1.0"

_PROJECT_MARKERS = (".here", "CLAUDE.md", ".claude")


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from *start* (default: CWD) looking for project markers.

    Override with the ``R2_PROJECT_ROOT`` environment variable.
    """
    if env_root := os.environ.get("R2_PROJECT_ROOT"):
        return Path(env_root).resolve()

    start = (start or Path.cwd()).resolve()
    for marker in _PROJECT_MARKERS:
        d = start
        while d != d.parent:
            if (d / marker).exists():
                return d
            d = d.parent
    return start  # fallback to CWD

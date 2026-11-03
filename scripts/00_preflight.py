#!/usr/bin/env python3
"""Thin orchestrator: PIZ GLORIA preflight / environment verification.

Usage:
    uv run python scripts/00_preflight.py

Verifies that the BOND-API protocol is importable and that this film's pure
domain core resolves. Exits 0 on success, 1 on failure (with diagnostics).
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import bond_api  # noqa: E402
from on_her_majestys_secret_service.mission import CODENAME, FILM, MissionProvider  # noqa: E402


def main() -> int:
    provider = MissionProvider()
    brief = provider.brief()
    print(f"Film: {FILM} · codename {CODENAME}")
    print(f"bond_api {bond_api.__version__}")
    print(f"Python {platform.python_version()} on {platform.platform()}")
    print(f"Objectives ({len(brief.objectives)}): {', '.join(brief.objectives)}")
    print(f"Assets ({len(brief.assets)}): {', '.join(a.name for a in brief.assets)}")
    print(
        f"Constraints ({len(brief.constraints)}): {', '.join(c.kind for c in brief.constraints)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

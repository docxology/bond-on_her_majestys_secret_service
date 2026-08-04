#!/usr/bin/env python3
"""Thin orchestrator: PIZ GLORIA mission phase 01 — brief.

Usage:
    uv run python scripts/01_brief.py

Prints the mission's declared objectives, assets, and constraints.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from on_her_majestys_secret_service.mission import MissionProvider  # noqa: E402


def main() -> int:
    brief = MissionProvider().brief()
    print(f"Film: {brief.film} · codename {brief.codename}")
    print(f"Objectives ({len(brief.objectives)}):")
    for objective in brief.objectives:
        print(f"  - {objective}")
    print(f"Assets ({len(brief.assets)}):")
    for asset in brief.assets:
        print(f"  - {asset.kind}:{asset.name}")
    print(f"Constraints ({len(brief.constraints)}):")
    for constraint in brief.constraints:
        print(f"  - {constraint.kind}: {constraint.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

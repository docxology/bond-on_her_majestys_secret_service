#!/usr/bin/env python3
# ruff: noqa: N999
# The numbered name `05_debrief` is the documented phase interface (AGENTS.md,
# README.md and the skill); renaming the file would break the documented
# invocation, so the name is kept and the finding is ignored here.
"""Thin orchestrator: PIZ GLORIA mission phase 05 — debrief.

Usage:
    uv run python scripts/05_debrief.py

Runs the full mission and prints the debrief lessons from the outcome.
"""

from __future__ import annotations

import sys
from pathlib import Path

from bond_api.protocol import ReconRequest, run_mission

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from on_her_majestys_secret_service.mission import MissionProvider


def main() -> int:
    debrief = run_mission(
        MissionProvider(), ReconRequest(goal="debrief the PIZ GLORIA mission")
    )
    print(f"Mission success: {debrief.outcome.success}")
    print(f"Lessons ({len(debrief.lessons)}):")
    for lesson in debrief.lessons:
        print(f"  - {lesson}")
    print(f"Input hash: {debrief.outcome.provenance.input_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# ruff: noqa: N999
# The numbered name `03_plan` is the documented phase interface (AGENTS.md,
# README.md and the skill); renaming the file would break the documented
# invocation, so the name is kept and the finding is ignored here.
"""Thin orchestrator: PIZ GLORIA mission phase 03 — plan.

Usage:
    uv run python scripts/03_plan.py

Prints the deterministic execution plan derived from the mission brief.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from on_her_majestys_secret_service.mission import MissionProvider


def main() -> int:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    print(f"Plan steps ({len(plan.steps)}):")
    for step in plan.steps:
        print(f"  - {step.name}: {step.action} {step.params}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

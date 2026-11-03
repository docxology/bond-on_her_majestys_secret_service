#!/usr/bin/env python3
# ruff: noqa: N999
# The numbered name `02_recon` is the documented phase interface (AGENTS.md,
# README.md and the skill); renaming the file would break the documented
# invocation, so the name is kept and the finding is ignored here.
"""Thin orchestrator: PIZ GLORIA mission phase 02 — recon.

Usage:
    uv run python scripts/02_recon.py ["recon goal", ...]

Runs reconnaissance and prints the findings; the goal defaults to a survey of
the domain.
"""

from __future__ import annotations

import sys
from pathlib import Path

from bond_api.protocol import ReconRequest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from on_her_majestys_secret_service.mission import MissionProvider


def main() -> int:
    goal = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "survey available models and constraints"
    )
    report = MissionProvider().recon(ReconRequest(goal=goal))
    print(f"Recon goal: {goal}")
    print(f"Findings ({len(report.findings)}):")
    for finding in report.findings:
        print(f"  - {finding.label}: {finding.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

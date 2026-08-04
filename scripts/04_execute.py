#!/usr/bin/env python3
"""Thin orchestrator: PIZ GLORIA mission phase 04 — execute.

Usage:
    uv run python scripts/04_execute.py

Executes the full deterministic mission (dispersion, alpine route, cover
identity), prints the results, and writes the JSON outcome + a dispersion
figure under ``output/``. Exits non-zero if the mission did not succeed.
"""

from __future__ import annotations

import sys
from pathlib import Path

from bond_api.serialization import to_json

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from on_her_majestys_secret_service.figures import render_dispersion_figure  # noqa: E402
from on_her_majestys_secret_service.mission import SCENARIO, MissionProvider  # noqa: E402


def main() -> int:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    outcome = provider.execute(plan)
    outcome_json = to_json(outcome)

    output_root = ROOT / "output"
    data_dir = output_root / "data"
    fig_dir = output_root / "figures"
    data_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    outcome_path = data_dir / "piz_gloria_outcome.json"
    outcome_path.write_text(outcome_json + "\n", encoding="utf-8")

    fig_path = render_dispersion_figure(SCENARIO, fig_dir / "aerosol_plume.png")

    disp = outcome.results["dispersion"]
    alpine = outcome.results["alpine"]
    cover = outcome.results["cover"]
    print(f"Mission success: {outcome.success}")
    print(
        f"Isopleth reach: {disp['isopleth_reach_m']} m · peak {disp['peak_concentration_kg_m3']} "
        f"kg/m3 at {disp['peak_distance_m']} m"
    )
    print(
        f"Alpine route: found={alpine['route_found']} distance={alpine['route_distance_m']} m "
        f"mean_grade={alpine['route_mean_grade_deg']} deg safe={alpine['route_safe']}"
    )
    print(f"Bray cover: score={cover['bray_score']} verdict={cover['bray_verdict']}")
    print(f"Outcome JSON -> {outcome_path}")
    print(f"Figure -> {fig_path}")
    print(f"Provenance input_hash: {outcome.provenance.input_hash}")
    return 0 if outcome.success else 1


if __name__ == "__main__":
    raise SystemExit(main())

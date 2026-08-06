#!/usr/bin/env python3
"""Thin orchestrator: PIZ GLORIA mission phase 04 — execute.

Usage:
    uv run python scripts/04_execute.py

Executes the full deterministic mission (plume + puff dispersion, alpine route
+ bobsleigh descent, Bray cover + timeline), prints the results, and writes the
JSON outcome plus figures under ``output/``. Exits non-zero if the mission did
not succeed.
"""

from __future__ import annotations

import sys
from pathlib import Path

from bond_api.serialization import to_json

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from on_her_majestys_secret_service.descent_dynamics import (  # noqa: E402
    canonical_bobsleigh_track,
    descent_simulation,
)
from on_her_majestys_secret_service.figures import (  # noqa: E402
    render_descent_figure,
    render_dispersion_figure,
    render_puff_figure,
    render_route_figure,
)
from on_her_majestys_secret_service.mission import (  # noqa: E402
    SCENARIO,
    MissionProvider,
)


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
    puff_fig = render_puff_figure(SCENARIO, fig_dir / "puff_footprint.png")
    descent_full = descent_simulation(canonical_bobsleigh_track())
    descent_fig = render_descent_figure(descent_full, fig_dir / "descent_profile.png")
    route_fig = render_route_figure(
        {"waypoints": outcome.results["alpine"]["waypoints"]},
        fig_dir / "route_profile.png",
    )

    disp = outcome.results["dispersion"]
    alpine = outcome.results["alpine"]
    cover = outcome.results["cover"]
    puff = disp["puff"]
    descent = alpine["descent"]
    bobsleigh = alpine["bobsleigh"]
    timeline = cover["timeline"]
    print(f"Mission success: {outcome.success}")
    print(
        f"Isopleth reach: {disp['isopleth_reach_m']} m · peak {disp['peak_concentration_kg_m3']} "
        f"kg/m3 at {disp['peak_distance_m']} m"
    )
    print(f"Puff arrival at {puff['arrival_time_s']} s · peak {puff['peak_concentration_kg_m3']} kg/m3")
    print(
        f"Alpine route: found={alpine['route_found']} distance={alpine['route_distance_m']} m "
        f"mean_grade={alpine['route_mean_grade_deg']} deg safe={alpine['route_safe']}"
    )
    print(f"Descent: {descent['total_time_s']} s, max {descent['max_speed_m_s']} m/s")
    print(
        f"Bobsleigh: max lateral {bobsleigh['max_lateral_g']} g (safe={bobsleigh['safe']}); "
        f"banked cornering {bobsleigh['banked_max_speed_m_s']} m/s at R={bobsleigh['hairpin_radius_m']} m"
    )
    print(
        f"Bray cover: score={cover['bray_score']} verdict={cover['bray_verdict']} "
        f"timeline={timeline['verdict']} ({timeline['coverage']})"
    )
    print(f"Outcome JSON -> {outcome_path}")
    print(f"Figures -> {fig_path}, {puff_fig}, {descent_fig}, {route_fig}")
    print(f"Provenance input_hash: {outcome.provenance.input_hash}")
    return 0 if outcome.success else 1


if __name__ == "__main__":
    raise SystemExit(main())

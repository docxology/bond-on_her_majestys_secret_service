"""PIZ GLORIA — the :class:`MissionProvider` adapter for OHMSS (1969).

This module is the thin bridge between the pure domain core and the frozen
``bond_api`` protocol. It implements every stage of the lifecycle:

* :meth:`MissionProvider.brief` — the mission definition (objectives, assets,
  constraints).
* :meth:`MissionProvider.recon` — findings derived from recon of the domain.
* :meth:`MissionProvider.plan` — the deterministic execution plan.
* :meth:`MissionProvider.execute` — runs the plan against the real domain
  modules and returns a fully-provenanced outcome.
* :meth:`MissionProvider.debrief` — lessons learned.

``execute`` is deterministic: it computes, from real functions, the aerosol
plume's isopleth reach *and its time-dependent puff footprint*, the alpine
route's slope safety *and its bobsleigh descent kinetics*, and the Bray
persona's cover score *and its timeline consistency*. Provenance (fixed
version + seed, input hash) is recorded for every outcome. The public protocol
shape is stable: ``film``, the five methods, and the ``register_gadgets``
hook (module-level :data:`REGISTRY`) are unchanged.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, cast

from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    MissionProvider as MissionProviderProtocol,
    Provenance,
    ReconReport,
    ReconRequest,
    Step,
)
from bond_api.registry import GadgetRegistry

from on_her_majestys_secret_service.alpine_routes import alpine_elevation, plan_safe_route
from on_her_majestys_secret_service.cover_identity import bray_persona, cover_score
from on_her_majestys_secret_service.descent_dynamics import (
    banked_curve_max_speed,
    canonical_bobsleigh_track,
    curve_radii,
    descent_over_waypoints,
    descent_simulation,
    track_curvature_audit,
)
from on_her_majestys_secret_service.dispersion_model import (
    PlumeScenario,
    isopleth_distance,
    peak_ground_concentration,
    stability_class,
)
from on_her_majestys_secret_service.identity_timeline import (
    canonical_timeline,
    timeline_consistency,
)
from on_her_majestys_secret_service.puff_dispersion import (
    arrival_time,
    puff_field_time_series,
)

__all__ = ["CODENAME", "FILM", "MissionProvider", "REGISTRY", "register_gadgets", "run_scenario"]

#: Film slug — the top-level import name under which the orchestrator
#: discovers this package (``import on_her_majestys_secret_service.mission``).
FILM = "on_her_majestys_secret_service"
#: Mission codename.
CODENAME = "PIZ GLORIA"
#: Package version mirrored in ``pyproject.toml`` (single source of truth here).
PACKAGE_VERSION = "0.1.0"
#: Deterministic seed used for any RNG-backed submodel (0 disables randomness).
SEED = 7

#: Canonical PIZ GLORIA release scenario used across the mission.
SCENARIO = PlumeScenario(
    release_rate=0.05,  # kg/s aerosolised allergen emission
    wind_speed=4.0,  # m/s
    release_height=25.0,  # m (valley-top release)
    stability=stability_class(4.0, daytime=True),
    valley=400.0,  # m channeling depth
)

#: Downwind receptor used for the puff early-warning analysis [m].
PUFF_RECEPTOR_X = 2000.0
#: Puff arrival threshold [kg/m^3] for the early-warning metric.
PUFF_THRESHOLD = 1e-8


def _route() -> dict[str, Any]:
    """Compute the planned safe alpine exfiltration route."""
    return cast(
        dict[str, Any],
        plan_safe_route(
            start=(5, 5),
            goal=(34, 35),
            max_slope=30.0,
            grid=40,
            elevation_func=alpine_elevation,
        ),
    )


def run_scenario() -> dict[str, Any]:
    """Compute the deterministic mission results from the real domain core.

    Returns a nested mapping holding the dispersion (plume + puff), alpine
    (route + descent + bobsleigh curve), and cover (score + timeline) results.
    Exposed as a module function so scripts and tests share the exact executed
    payload without reaching into the provider's private helpers.
    """
    isopleth = isopleth_distance(1e-7, SCENARIO, max_distance=50000.0)
    peak_x, peak_c = peak_ground_concentration(SCENARIO)

    puff_series = puff_field_time_series(
        SCENARIO,
        PUFF_RECEPTOR_X,
        0.0,
        1.5,
        t_start=0.0,
        t_end=1500.0,
        dt=10.0,
    )
    puff_arrival = arrival_time(puff_series, PUFF_THRESHOLD)
    puff_conc = puff_series["concentration"]

    route = _route()
    waypoints = cast(list[Any], route.get("waypoints", []))
    bobsleigh_track = canonical_bobsleigh_track()
    descent = descent_simulation(bobsleigh_track)
    audit = track_curvature_audit(bobsleigh_track)
    radii = [r for r in curve_radii(bobsleigh_track) if r != float("inf")]
    hairpin_radius = min(radii) if radii else 30.0
    banked_max_speed = banked_curve_max_speed(float(hairpin_radius), 55.0)

    persona = cast(dict[str, Any], bray_persona())
    claims, observations = canonical_timeline()
    timeline = timeline_consistency(claims, observations)

    return {
        "dispersion": {
            "isopleth_reach_m": round(float(isopleth), 2),
            "peak_concentration_kg_m3": round(float(peak_c), 12),
            "peak_distance_m": round(float(peak_x), 2),
            "scenario_stability": SCENARIO.stability,
            "puff": {
                "arrival_time_s": float(puff_arrival) if puff_arrival is not None else None,
                "peak_concentration_kg_m3": round(float(max(puff_conc)), 12),
                "steady_concentration_kg_m3": round(float(puff_conc[-1]), 12),
            },
        },
        "alpine": {
            "route_found": bool(route["found"]),
            "route_distance_m": float(route["distance"]),
            "route_mean_grade_deg": float(route["mean_grade_deg"]),
            "route_safe": bool(route["safe"]),
            "waypoints": waypoints,
            "descent": {
                "total_time_s": float(descent["total_time_s"]),
                "max_speed_m_s": float(descent["max_speed_m_s"]),
                "distance_m": float(descent["total_distance_m"]),
            },
            "bobsleigh": {
                "max_lateral_g": float(audit["max_lateral_g"]),
                "over_g": int(audit["over_g"]),
                "safe": bool(audit["safe"]),
                "banked_max_speed_m_s": round(float(banked_max_speed), 3),
                "hairpin_radius_m": round(float(hairpin_radius), 2),
            },
        },
        "cover": {
            "bray_score": persona["score"],
            "bray_verdict": persona["verdict"],
            "forensic_overlap_risk": round(float(persona["profile"]["forensic_overlap"]), 6),
            "timeline": {
                "coverage": float(timeline["coverage"]),
                "conflicts": int(timeline["conflicts"]),
                "verdict": timeline["verdict"],
                "held": bool(timeline["held"]),
            },
        },
    }


def _input_hash() -> str:
    """Stable fingerprint of the mission inputs (scenario + seed + version)."""
    payload = {
        "release_rate": SCENARIO.release_rate,
        "wind_speed": SCENARIO.wind_speed,
        "release_height": SCENARIO.release_height,
        "stability": SCENARIO.stability,
        "valley": SCENARIO.valley,
        "seed": SEED,
        "version": PACKAGE_VERSION,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


class MissionProvider(MissionProviderProtocol):  # noqa: N801 — name fixed by discovery contract
    """Deterministic OHMSS PIZ GLORIA mission provider (protocol adapter)."""

    film = FILM

    def brief(self) -> MissionBrief:
        """Declare the PIZ GLORIA mission: six objectives, six assets."""
        return MissionBrief(
            film=self.film,
            codename=CODENAME,
            objectives=(
                "model aerosol bioweapon dispersion in the valley",
                "resolve the plume's time-dependent puff footprint",
                "plan a safe alpine exfiltration route",
                "simulate the bobsleigh descent and banked-curve clearance",
                "score the Bray cover identity",
                "verify the Bray timeline against observed sightings",
            ),
            assets=(
                Asset(kind="model", name="dispersion", payload={"scenario": "gaussian-plume"}),
                Asset(kind="model", name="puff-dispersion", payload={"model": "lagrangian-gaussian"}),
                Asset(kind="model", name="alpine-routes", payload={"planner": "dijkstra-safe"}),
                Asset(kind="model", name="descent-dynamics", payload={"model": "point-mass-bobsleigh"}),
                Asset(kind="model", name="cover-identity", payload={"persona": "bray"}),
                Asset(kind="model", name="identity-timeline", payload={"method": "interval-verification"}),
            ),
            constraints=(
                Constraint(kind="determinism", detail="no random draws, no external calls"),
                Constraint(kind="real-data", detail="results computed from real domain functions"),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the domain capabilities relevant to the recon goal."""
        return ReconReport(
            findings=(
                Finding(label="goal", detail=request.goal),
                Finding(label="dispersion", detail="Gaussian plume + valley channeling + puff dynamics"),
                Finding(label="alpine", detail="Dijkstra safe-route planner + bobsleigh descent dynamics"),
                Finding(label="cover", detail="weighted Bray-persona risk + timeline verification"),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the six deterministic analysis steps."""
        return MissionPlan(
            steps=(
                Step(
                    name="dispersion",
                    action="compute_plume_footprint",
                    params={"objective": len(brief.objectives)},
                ),
                Step(name="puff", action="resolve_puff_time_series", params={"receptor_x": PUFF_RECEPTOR_X}),
                Step(name="alpine", action="plan_safe_route", params={"max_slope": 30.0}),
                Step(name="descent", action="simulate_descent", params={"mass": 100.0}),
                Step(name="cover", action="score_cover_identity", params={"persona": "bray"}),
                Step(name="timeline", action="verify_cover_timeline", params={"method": "interval"}),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the plan against the real domain core; return provenanced outcome."""
        results = run_scenario()
        results["steps_completed"] = len(plan.steps)
        results["outputs"] = tuple(step.name for step in plan.steps)
        return MissionOutcome(
            success=True,
            results=results,
            provenance=Provenance(
                package_version=PACKAGE_VERSION,
                seed=SEED,
                input_hash=_input_hash(),
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Summarize the mission and record the standing alpine-ops lessons."""
        return Debrief(
            outcome=outcome,
            lessons=(
                "high stability classes suppress vertical dispersion and extend valley reach",
                "puff arrival precedes plume steady-state — early warning is real",
                "safe alpine exfiltration must gate on grade before curvature",
                "unbanked bobsleigh hairpins exceed lateral-g ceilings at sprint speed",
                "the Bray persona is defensible only while forensic overlap stays low",
                "one contradicting sighting unseats an otherwise-covered timeline",
            ),
        )


#: Module-level registry so the orchestrator can inspect gadgets.
REGISTRY = GadgetRegistry()


def register_gadgets(registry: GadgetRegistry | None = None) -> GadgetRegistry:
    """Register the film's deterministic gadgets onto a registry (default the
    module-level :data:`REGISTRY`) and return it."""
    target = registry if registry is not None else REGISTRY
    target.register(
        FILM,
        {
            "dispersion_model": SCENARIO,
            "plume_footprint": isopleth_distance,
            "puff_time_series": puff_field_time_series,
            "alpine_planner": plan_safe_route,
            "descent_simulator": descent_over_waypoints,
            "bobsleigh_audit": track_curvature_audit,
            "cover_risk": cover_score,
            "timeline_verifier": timeline_consistency,
        },
    )
    return target


# Auto-register on import so discovery surfaces the gadgets immediately.
register_gadgets()

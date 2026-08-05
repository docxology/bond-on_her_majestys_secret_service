# TODO — on_her_majestys_secret_service (PIZ GLORIA)

## Built — phase 2 (core)

* `dispersion_model.py` — Gaussian-plume aerosol dispersion with
  Pasquill-Gifford stability coefficients and valley-channeled transport.
* `alpine_routes.py` — bobsleigh-grade track geometry, segment safety tiers,
  and a slope-safety-gated Dijkstra route planner.
* `cover_identity.py` — weighted cover-identity risk scoring for the Bray
  persona.
* `mission.py` — `MissionProvider` adapter; `manuscript_variables.py`;
  `figures/`; per-phase `scripts/`; core test suites.

## Built — phase 4 (deepened)

* `puff_dispersion.py` — **new**: Lagrangian Gaussian puff train
  (time-dependent dispersion). Superimposes discrete mass puffs at a downstream
  receptor to yield a concentration time series, arrival time (early-warning),
  transient peak, and integrated dose. Provably converges to the steady plume
  far downwind (cross-checked in tests). Functions: `single_puff`,
  `puff_field_time_series`, `arrival_time`, `puff_concentration_series`,
  `peak_of_series`, `integrated_exposure`.
* `descent_dynamics.py` — **new**: point-mass bobsleigh descent. Integrates
  `a(v)=g·sinθ−μ·g·cosθ−k·v²` along a track profile with friction + drag;
  adds curve physics (`lateral_gaccel`, `banked_curve_max_speed`), local
  curvature radii, a combined `track_curvature_audit` (speed profile × radii
  vs a lateral-g ceiling), the canonical deterministic bobsleigh track, and a
  waypoint-shape helper.
* `identity_timeline.py` — **new**: cover-timeline verification. Interval
  arithmetic over claimed vs observed events (`TimelineEvent`); computes
  matched minutes, coverage, contradictions, a discrete verdict, and
  uncovered (no-alibi) windows. `canonical_timeline()` is the single source of
  truth shared by mission + tests.
* `mission.py` — deepened inside while keeping the public protocol shape:
  six objectives/assets/plan-steps, richer `run_scenario()` results
  (dispersion.puff, alpine.descent, alpine.bobsleigh, cover.timeline), and six
  debrief lessons. `film`, the five methods, and `register_gadgets`/`REGISTRY`
  are unchanged.
* `manuscript_variables.py` — nine new `PIZ_*` tokens (puff arrival/peak,
  descent time/speed, banked speed, track g/status, timeline
  coverage/conflicts/verdict).
* `figures/` — new `render_puff_figure` and `render_descent_figure`;
  `scripts/04_execute.py` renders all three figures.

## Integration points (declared)

1. **`bond-api` protocol**: the `MissionProvider` in `mission.py` is built
   against the frozen `bond_api` types and registered via `[tool.uv.sources]`
   path dependency. Contract is frozen; no further work expected.
2. **Gadget registry**: the film registers eight gadgets (dispersion_model,
   plume_footprint, puff_time_series, alpine_planner, descent_simulator,
   bobsleigh_audit, cover_risk, timeline_verifier) into a
   `bond_api.GadgetRegistry`; wire these into a coordinator's gadget inventory
   when the coordinator is ready.
3. **Provenance persistence**: outcomes currently carry `Provenance` in-memory;
   once `bond_utilities.mission_io.record_provenance_outcome` is available to
   downstream packages, `scripts/04_execute.py` can delegate the on-disk
   record to it.
4. **Surveyed terrain**: `alpine_routes` and `descent_dynamics` use analytic
   test surfaces; swap `elevation_func` / the canonical track for surveyed
   rasters to move from illustrative to operational routing.

## Follow-ups

* Add a lateral load-transfer / steering term to `descent_dynamics` (beyond
  the planar 1-D model).
* Wire `render_route_figure` into `scripts/04_execute.py` alongside the other
  figures.

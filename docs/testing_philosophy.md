# Testing philosophy — PIZ GLORIA

This package is tested with **real data and real computation only**. There is
no mock framework anywhere. The approach:

## Per-concept real-data suites

* `test_dispersion_model.py` — Gaussian-plume physics vs the cited
  Pasquill-Gifford table, reach monotonicity, crosswind decay, wind/rate
  scaling, valley channeling, validation branches.
* `test_puff_dispersion.py` — single-puff symmetry/peak, series shape, the
  **steady-state convergence cross-check** (puff train ≈ plume far downwind),
  arrival time, summary/peak/integrated-exposure, validation branches,
  determinism.
* `test_alpine_routes.py` — geometry (distance, slope, Menger curvature),
  safety tiers, route safety report, planner feasibility / slope gate /
  impassable barrier / flat-shortest path.
* `test_descent_dynamics.py` — banked-curve speed limit, lateral g, curvature
  radii, the point-mass descent (friction sensitivity, waypoint speeds,
  determinism, error branches, step cap), track audit (flat safe / hairpin
  over-limit), canonical track determinism.
* `test_cover_identity.py` — weighted score, verdicts, breach inflation,
  canonical Bray persona, validation branches.
* `test_identity_timeline.py` — event validation, matched/conflict/coverage,
  held-high vs low vs empty cases, uncovered windows, canonical timeline.

## Protocol & integration

* `test_mission.py` — drives the real `MissionProvider` through the protocol
  (brief/recon/plan/execute/debrief), asserts the deepened six-step shape,
  determinism, provenance fields, `run_mission` flow, serialization
  round-trip, `bond_api` discovery by slug, and the eight-gadget registration.

## Manuscript gates

* `test_manuscript_variables.py` — a **live cross-reference**: every
  `{{TOKEN}}` in `manuscript/[0-9]*.md` must be produced by
  `generate_variables()`. Strict resolution forbids leftover `{{TOKEN}}`.

## Scripts & figures

* `test_scripts_smoke.py` — subprocess-invokes each real mission-phase CLI
  (`sys.executable`, cwd=root) and asserts exit codes, stdout, and produced
  artifacts under `output/`. Includes a no-mock scan of the tree.
* `test_figures.py` — renders real PNGs headlessly (Agg) — plume, puff, route,
  and descent figures — and asserts they exist and are non-trivial.

## Determinism

All tests use fixed inputs; nothing depends on the wall clock or on shared
RNG state. The executed mission is asserted to be byte-deterministic
(`run_scenario() == run_scenario()`), as are each module's canonical outputs.

## Coverage gate

`uv run python -m pytest tests/ --cov=src --cov-fail-under=90` enforces the
>=90% line+branch floor on `src/`.

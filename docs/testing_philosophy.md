# Testing philosophy — PIZ GLORIA

This package is tested with **real data and real computation only**. There is
no mock framework anywhere. The approach:

## Per-concept real-data suites

* `test_dispersion_model.py` — verifies the Gaussian-plume physics against the
  cited Pasquill-Gifford coefficient table, monotonicity of reach with
  threshold, crosswind decay, wind/release-rate scaling, valley channeling,
  and every input-validation branch.
* `test_alpine_routes.py` — verifies geometry (distance, slope, Menger
  curvature), segment safety tiers, the route safety report, and the planner
  (feasible route found, slope gate respected, impassable barrier → not found,
  flat terrain → shortest path).
* `test_cover_identity.py` — verifies the weighted score, verdicts, breach
  inflation, the canonical Bray persona, and validation branches.

## Protocol & integration

* `test_mission.py` — drives the real `MissionProvider` through the protocol
  (brief/recon/plan/execute/debrief), asserts determinism, provenance fields,
  `run_mission` flow, serialization round-trip, `bond_api` discovery by slug,
  and gadget registration.

## Manuscript gates

* `test_manuscript_variables.py` — a **live cross-reference**: every
  `{{TOKEN}}` in `manuscript/[0-9]*.md` must be produced by
  `generate_variables()`. Strict resolution forbids leftover `{{TOKEN}}`.

## Scripts & figures

* `test_scripts_smoke.py` — subprocess-invokes each real mission-phase CLI
  (`sys.executable`, cwd=root) and asserts exit codes, stdout, and produced
  artifacts under `output/`. Includes a no-mock scan of the tree.
* `test_figures.py` — renders real PNGs headlessly (Agg) and asserts they
  exist and are non-trivial.

## Determinism

All tests use fixed inputs; nothing depends on the wall clock or on shared
RNG state. The executed mission is asserted to be byte-deterministic
(`run_scenario() == run_scenario()`).

## Coverage gate

`uv run python -m pytest tests/ --cov=src --cov-fail-under=90` enforces the
>=90% line+branch floor on `src/`.

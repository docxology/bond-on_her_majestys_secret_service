# tests/ — real data, real computation

A per-concept suite for each of the six domain modules, plus `test_mission.py`,
`test_figures.py`, `test_manuscript_variables.py` and `test_scripts_smoke.py`.

## Rules

- **No mock framework anywhere** — no `unittest.mock`, no `MagicMock`, no monkey-patching.
  Tests use real computation on real, fixed or deterministically generated data.
- **Each suite states the physics it checks.** For example the puff suite covers single-puff
  symmetry and peak, the steady-state convergence cross-check (puff train against the plume
  far downwind), arrival time and determinism; the descent suite covers banked-curve speed
  limit, lateral g, the point-mass descent and the track audit. A new domain module needs a
  suite in the same style.
- **`test_mission.py` drives the real `MissionProvider`** through brief, recon, plan, execute
  and debrief against the frozen protocol; it is the integration tripwire.
- **Deterministic** — fixed seeds, byte-identical scenario results.
- Coverage floor 90% line and branch: `uv run python -m pytest tests/ --cov=src --cov-fail-under=90 -q`.

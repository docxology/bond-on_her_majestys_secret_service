---
name: on-her-majestys-secret-service
description: Build/maintain the on_her_majestys_secret_service (PIZ GLORIA) PROJECT BOND film package — aerosol dispersion, alpine routes, cover identity.
---

# on-her-majestys-secret-service — PIZ GLORIA

PROJECT BOND film package for *On Her Majesty's Secret Service* (1969), mission
codename PIZ GLORIA. Scope = this directory only; path-scoped commits, and
`origin` is the published GitHub repo (`docxology/bond-on_her_majestys_secret_service`)
— never force-push.

## Concepts

- `src/on_her_majestys_secret_service/dispersion_model.py` — steady-state
  aerosol (allergen) dispersion: Gaussian plume, Pasquill–Gifford stability
  classes, valley-channeled transport.
- `src/on_her_majestys_secret_service/puff_dispersion.py` — time-resolved
  dispersion: Lagrangian Gaussian puff train superposition and arrival times.
- `src/on_her_majestys_secret_service/alpine_routes.py` — track geometry plus
  slope-safety-gated Dijkstra route planning.
- `src/on_her_majestys_secret_service/descent_dynamics.py` — bobsleigh descent
  kinematics, lateral g, banked-curve speed limit.
- `src/on_her_majestys_secret_service/cover_identity.py` — weighted additive
  cover-identity (Bray persona) risk scoring.
- `src/on_her_majestys_secret_service/identity_timeline.py` — cover-timeline
  interval-coverage verification.
- `src/on_her_majestys_secret_service/mission.py` — BOND-API `MissionProvider`
  adapter (film `on_her_majestys_secret_service`, codename `PIZ GLORIA`), gadget
  registration, deterministic provenance.
- `manuscript_variables.py` (token map), `figures/dispersion.py` (one renderer
  per concept model), thin `scripts/` CLIs — current counts are in
  `docs/_generated/COUNTS.md`.

## Quick reference

```bash
uv sync --extra dev   # resolves the local ../bond-api path dependency
uv run python -m pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/04_execute.py
uv run python scripts/z_generate_manuscript_variables.py
```

## Pitfalls

- Keep the pure domain core importable WITHOUT bond-api; only `mission.py`
  imports it.
- Inject all result metrics as `{{TOKEN}}`s; never hand-author numbers in prose.
- The mission adapter uses `bond_api` (FROZEN) — do not invent protocol types,
  and do not change the public shape of `mission.py`.
- Zero mocks; fixed seed; no wall-clock time in persisted artifacts; `output/`
  is git-ignored.

## Cross-refs

- Package contract: [`AGENTS.md`](../../../AGENTS.md)
- README: [`README.md`](../../../README.md)
- Open work: [`TODO.md`](../../../TODO.md)
- Architecture: [`docs/architecture.md`](../../../docs/architecture.md)

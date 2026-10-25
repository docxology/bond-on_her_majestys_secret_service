# AGENTS.md — PIZ GLORIA (on_her_majestys_secret_service)

This is a PROJECT BOND film package (mission codename **PIZ GLORIA**, from
*On Her Majesty's Secret Service*, 1969) converted from the template exemplar
scaffold. It implements a `MissionProvider` against the frozen `bond_api`
protocol and ships a pure, deterministic, mock-free scientific domain core of
**six** concept modules (phase-4 deepened).

## Scope & guardrails

* Work only inside this package directory. Never touch sibling packages, bond
  root files, or the template repo.
* **Published, never rewritten**: `origin` is the GitHub repo
  (`docxology/bond-on_her_majestys_secret_service`); push through the vault
  tool, never force-push or rewrite history.
* Path-scoped commits; `git add -A` inside this repo only.
* **No mock framework** (no `unittest.mock`, `MagicMock`, monkey-patching).
  All tests use real data + computation.
* >=90% line+branch coverage on `src/`:
  `uv run python -m pytest tests/ --cov=src --cov-fail-under=90`.
* Deterministic: fixed seeds, no untracked RNG, no wall-clock in artifacts.
* Thin orchestrators in `scripts/`; business logic in `src/`.
* Type hints + docstrings; `ruff` and `mypy` clean on `src/` and `scripts/`.
* Manuscript variables injected from `manuscript/config.yaml` +
  `src/.../manuscript_variables.py` — never hand-author metrics in prose.
* **Protocol stability**: the public shape of `mission.py` is stable — `film`,
  the five `MissionProvider` methods, and the `register_gadgets` hook /
  module-level `REGISTRY` are unchanged. Deepening happens inside the package
  (new modules, richer mission internals).

## Layer contract

| Surface | Rule |
| --- | --- |
| Domain core (`dispersion_model.py`, `puff_dispersion.py`, `alpine_routes.py`, `descent_dynamics.py`, `cover_identity.py`, `identity_timeline.py`) | Pure math; no `bond_api`, no I/O, no `infrastructure` imports. Importable standalone. |
| `mission.py` | Thin adapter; imports `bond_api` protocol + the pure domain. |
| `manuscript_variables.py`, `figures/` | Derive from the domain / protocol; may do file I/O. |
| `scripts/` | Thin CLIs (sys.path bootstrap + invoke). |

The domain core must remain importable **without** `bond-api`, so a failure of
the path dependency never blocks the pure science.

## Protocol integration

`src/on_her_majestys_secret_service/mission.py` exposes `MissionProvider`
(module top level) implementing `brief / recon / plan / execute / debrief`
with the frozen `bond_api` dataclasses. It registers gadgets (dispersion, puff,
alpine planner, descent, bobsleigh audit, cover risk, timeline verifier) into a
`GadgetRegistry`. `pyproject.toml` declares the local path dependency:
`bond-api = { path = ".../bond/bond-api" }` under `[tool.uv.sources]`. Run
`uv sync --extra dev` before `pytest`.

## Verification (before done)

```bash
uv run python -m pytest tests/ --cov=src --cov-fail-under=90 -q
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
# lineage: no exemplar strings
rg -n "template_?" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
git status --short   # clean after commit
```

## Mission phases

`scripts/01_brief.py` .. `scripts/05_debrief.py` are the per-phase CLIs;
`scripts/00_preflight.py` verifies the environment; `scripts/z_generate_manuscript_variables.py`
hydrates the manuscript tokens.

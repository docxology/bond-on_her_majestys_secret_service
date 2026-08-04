# Agent instructions — PIZ GLORIA

Read this before modifying the package. This is the operational contract for
agents working inside `on_her_majestys_secret_service`.

## Hard rules

1. **Scope**: work only inside this directory. Do not modify sibling BOND
   packages, bond root files, or the parent template repo.
2. **Local-only**: there is no git remote. Never push. Commit path-scoped
   (`git add -A` inside this repo only).
3. **Deterministic**: fixed seeds; no untracked random draws; no wall-clock
   time in persisted artifacts. `run_scenario()` must return byte-identical
   results across runs.
4. **No mocks**: no `unittest.mock`, `MagicMock`, or monkey-patching anywhere
   in `src/`, `scripts/`, or `tests/`. Tests use real computation with real
   (fixed or deterministically generated) data.
5. **>=90% coverage**: `uv run python -m pytest tests/ --cov=src --cov-fail-under=90`
   must pass, on both lines and branches.
6. **Layer contract**: the pure domain modules (`dispersion_model.py`,
   `alpine_routes.py`, `cover_identity.py`) must not import `bond_api`,
   `infrastructure`, or perform I/O; they stay importable standalone. Only
   `mission.py` and downstream layers may touch `bond_api`.
7. **Thin scripts**: `scripts/` contains thin CLIs that bootstrap `sys.path`
   and delegate to `src/`. Business logic lives in `src/`.
8. **Manuscript tokens**: metrics flow through
   `src/on_her_majestys_secret_service/manuscript_variables.py`. Never
   hand-author a measured number in manuscript prose.
9. **Lineage**: the scaffold lineage string must not appear in tracked files
   outside explicit lineage documentation. `rg` should return nothing.
10. **Quality gates**: `ruff check` + `ruff format --check` + `mypy` on
    `src/` and `scripts/` must be clean.

## Mise-en-scène

The package models the PIZ GLORIA operation: an aerosolized allergen bioweapon
release and the alpine exfiltration route an agent would use under the *Bray*
cover. Treat the domain math seriously — it is real dispersion / routing /
risk science, not placeholder code.

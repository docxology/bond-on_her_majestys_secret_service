# scripts/ — the mission CLIs in order

`00_preflight.py`, then `01_brief.py`, `02_recon.py`, `03_plan.py`, `04_execute.py` and
`05_debrief.py`, plus `z_generate_manuscript_variables.py`.

## Rules

- **The numbering is the mission order.** Preflight checks the environment and the sibling
  `bond-api` path dependency first; running a later step against an unprepared environment
  produces a failure that looks like a domain bug.
- **Thin CLIs only**: argument parsing, printing and file writing, with a `sys.path` bootstrap.
  Business logic lives in `src/on_her_majestys_secret_service/`.
- **Regenerate tokens and figures after any structural change** with
  `uv run python scripts/z_generate_manuscript_variables.py`; the `z_` prefix marks the
  generator, which runs after the change it reflects.
- **Never hand-author a measured number in manuscript prose.** Metrics flow through
  `src/on_her_majestys_secret_service/manuscript_variables.py`.
- **Scope**: this package only; never sibling BOND packages, bond root files or the template
  repo. `tests/test_scripts_smoke.py` covers these entry points.

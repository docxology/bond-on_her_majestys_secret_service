# Live counts — PIZ GLORIA (on_her_majestys_secret_service)

Generated counts (do not hand-edit; re-run the test gate to refresh).

- Test count: 206 passed (0 skipped, 0 failed)
- Coverage (line + branch) on `src/`: 97.84% (837 statements, 276 branches,
  11 missed lines, 13 partial branches)
- Lint: `ruff check src/ scripts/ tests/` — All checks passed
- Format: `ruff format --check src/ scripts/ tests/` — 35 files already formatted
- Types: `mypy src/ scripts/` — no issues found in 20 source files
- Recorded copies: `scripts/vendor.py --check` — ok, 0 finding(s)

Measured 2026-11-04 on Python 3.15.1 with ruff 0.16.1 (the lock's pin).

Command:
```
uv run python -m pytest tests/ --cov=src --cov-fail-under=90
```

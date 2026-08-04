# Reproducibility {#sec:reproducibility}

## Determinism contract

The PIZ GLORIA mission is reproducible by construction:

* Fixed scenario parameters and fixed seed (`7`); randomness is disabled.
* No wall-clock time enters any persisted artifact (provenance `wall_time_s`
  is recorded as `0.0`).
* No mock framework anywhere in the source or tests — all tests are real data
  + computation.
* `output/` is regenerable and git-ignored: re-running
  `scripts/04_execute.py` and `scripts/z_generate_manuscript_variables.py`
  reproduces byte-identical artifacts (a live determinism proof).

## Provenance

Every executed outcome carries a `Provenance` record with package version,
seed, a SHA-256 `input_hash` over the sorted scenario inputs, and wall time.
The outcome is also serialized with the `bond_api` tagged-JSON format so it can
be audited without re-running the film.

## Test coverage

The suite enforces the >=90% line+branch coverage gate on `src/` via
`uv run pytest tests/ --cov=src --cov-fail-under=90`. Live counts and coverage
are tracked in `docs/_generated/COUNTS.md`.

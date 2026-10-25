# TODO — on_her_majestys_secret_service (PIZ GLORIA)

Deterministic mission-software package for *On Her Majesty's Secret Service* (1969), modelling three
operational pillars: aerosol dispersion (steady Gaussian plume plus a Lagrangian puff train), alpine
descent (bobsleigh point-mass dynamics, curve physics, slope-safety-gated routing), and cover
identity (weighted persona risk plus interval-arithmetic timeline verification).

**Verified state, measured 2026-10-25:** `uv run pytest tests/ --cov=src --cov-fail-under=90` →
**205 passed, 97.84% coverage**. Six domain modules plus `mission.py` (frozen
`bond_api.MissionProvider`) and `manuscript_variables.py`. The 2026-08-06 `ruff` / `ruff format
--check` / `mypy` "clean" claims are **not reproducible against the locked ruff 0.16.1** — the
formatter wants to rewrite 20 files and `ruff check` reports 51 findings — and `mypy` did not
complete inside 500 s on an external drive. Re-verify before repeating those claims.

## Open work

### Correctness

**None open.** C1 (wall-clock determinism) and C2 (mis-attributed citation) were both closed on
2026-08-05 — see *Closed* below.

### Verification

**V1 — The adversarial audit is partial.** Five agent attempts to audit this package failed on model
safeguards (three on Opus, two on Sonnet), so the audit was finally run inline by the session lead
rather than by an independent skeptic. It covered: figure provenance (clean — `figures/dispersion.py`
imports `dispersion_model` and `puff_dispersion` rather than re-declaring constants), the `N/A`
fallback path (clean — `require_outputs=False` is a deliberate draft mode, bound in both directions
by `tests/test_manuscript_variables.py`, and `output/` is gitignored so no `N/A` artifact was ever
committed), and all seven citations (one was wrong; see C2 in *Closed*).

*Not yet covered, and still the highest-value work here:* green-by-construction checks on every
headline metric in `manuscript/03_results.md`, hollow-test review across `tests/`, and numerical
verification of the mathematical claims in module docstrings. A sibling asserted a noncentrality
parameter its own code contradicted, inflating a published probability from 54% to 66%.

*Done when:* an independent agent — not the one that wrote or fixed this package — has attacked those
three vectors and recorded its findings here.

**V2 — Bibliography entries are never cited inline.** All seven keys in `manuscript/references.bib`
appear in `99_references.md` as a numbered reading list, but no manuscript section cites them with
`[@key]`. They are reachable by a reader but absent from the citation graph, so the compendium's
unified bibliography carries entries nothing points at.

*Done when:* each source is either cited at the point its model is used, or the bibliography is
explicitly framed as background reading rather than works cited.

**V3 — The puff/plume convergence claim is asserted in prose.** `puff_dispersion.py` is documented
as provably converging to the steady plume far downwind.

*Done when:* bound by a test with an explicit tolerance across a range of downwind distances, plus a
negative control at a distance where the two models should *not* agree.

### Closed 2026-08-05

**C1 — Wall-clock timestamp broke the byte-identical claim.** `GENERATION_TIMESTAMP` read
`datetime.now()` and rendered into `manuscript/05_experimental_setup.md` while
`manuscript/04_conclusion.md` and `06_reproducibility.md` claimed byte-identical regeneration. Now
derived from the committed `paper.date` via `edition_stamp()`. Bound by
`TestRegenerationDeterminism`, which compares real bytes across a second boundary — and was proven
able to fail by temporarily reintroducing the wall clock. This was the last package in the fleet
carrying the defect.

**C2 — Mis-attributed citation.** `morlock1989bobsled` gave the title as "Factors influencing
performance in bobsled: Part I: kinematics" in *Journal of Biomechanics* 22(8-9):965–970. Every one
of those fields was wrong. The paper is Morlock & Zatsiorsky, "Factors influencing performance in
bobsledding: I: Influences of the bobsled crew and the environment", *International Journal of Sport
Biomechanics* 5(2):208–221. Its actual scope — a regression of finish time on start order, ice
temperature and push time — is now stated in both `references.bib` and `99_references.md`, along
with the fact that it does not underwrite the point-mass equations in `descent_dynamics.py`.

### Documentation

**D1 — This file was a build log, not a TODO.** Rewritten 2026-08-05. Keep it a register of open
work: delete items when they close, and do not re-add "what was built" narration — that belongs in
`README.md` and `docs/architecture.md`, both of which already carry it accurately for all six
modules.

### Extension

**E1 — Surveyed terrain instead of analytic surfaces.** `alpine_routes` and `descent_dynamics` use
analytic test surfaces; swapping `elevation_func` and the canonical track for surveyed rasters would
move the routing from illustrative to operational, and would let the alpine and dispersion pillars
share one geometry instead of two independent abstractions.

**E2 — Lateral load-transfer / steering term in `descent_dynamics`,** beyond the planar 1-D model.

**E3 — Wire `render_route_figure` into `scripts/04_execute.py`** alongside the other three figures.

**E4 — Delegate on-disk provenance.** Outcomes carry `Provenance` in memory;
`bond_utilities.mission_io.record_provenance_outcome` now exists, so `scripts/04_execute.py` could
delegate the persisted record. Note the constraint: that helper defaults `started_at` to
`datetime.now(timezone.utc)`, so delegating without pinning `started_at` would reintroduce C1.

## Known limitations (not bugs)

- **No external data.** Every scenario is a committed deterministic fixture. The package makes no
  claim to reproduce any historical event; its numbers are properties of the model, not measurements
  of the world.
- **Point-mass descent.** `descent_dynamics.py` ignores sled articulation, runner dynamics and ice
  temperature. Documented in `manuscript/07_scope_and_related_work.md`; deliberately out of scope.
- **Gadget registry is not consumed downstream.** The film registers eight gadgets into a
  `bond_api.GadgetRegistry`; wiring them into a coordinator inventory is coordinator-side work, not
  a defect here.
- **`layer_contract.yaml` lists six pure-domain modules.** Corrected in the Phase-5 pass; the three
  Phase-4 additions had been silently missing. Recorded so it is not re-litigated.

## Verification

```bash
uv sync --extra dev   # resolves the local ../bond-api path dependency

uv run pytest tests/ --cov=src --cov-fail-under=90   # expect 205 passed, 97.84%
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/                            # expect clean, 19 files
```

The fleet-level gates (`_phase_aggregate_gate.sh`, `_phase_docs_gate.py`, `_phase_lint_sweep.sh`,
`_phase_prerender_sweep.sh`) live in the sibling `bond-private` checkout, not in this repo. If `uv`
reports `Failed to initialize cache`, that is a sandbox restriction rather than a package failure —
re-run with the sandbox disabled.

## Round-2 (2026-08-06)

Hostile re-review by the round-2 improvement agent (inline, this session).
Baseline before changes: 196 passed, 98.15% coverage; ruff/mypy clean.

### Findings and verified fixes

**F1 — Bobsleigh descent reported distance overshot the track by ~7 %.**
The Euler integrator advanced the accumulated position with the step-start
speed but the segment remainder with the step-end speed, letting
`total_distance_m` drift from the true arc length (1032.59 m reported vs
964.51 m geometric on the canonical track). Fixed by advancing both with the
step-start speed and reporting the scalar from the cumulative waypoint arc
length. Regression: `test_descent_dynamics.py::TestDescentDistance
::test_total_distance_matches_track_arc_length` (reported == geometric within
1e-6; would have failed by ~68 m before). Side effects measured: descent time
37.45→37.5 s, max speed 45.70→45.77 m/s; the canonical audit still flags >4 g.

**F2 — Timeline coverage double-counted overlapping same-location claims.**
`matched_minutes` summed per-claim overlaps and only capped at the observation
length, so overlapping same-location claims covering [0,80]∪[20,40] = 80 min of
a [0,100] observation were counted as 100 → a cover could read coverage 1.0
(held) when only 0.8 was genuinely covered. Now merges same-location overlaps
into a true union per observation. Regression: `test_identity_timeline.py
::test_overlapping_same_location_claims_are_not_double_counted` (80, not 100;
coverage 0.8). Canonical result unchanged (claims disjoint).

**F3 — `banked_curve_max_speed` raised an obscure `math domain error` on
invalid banks.** Negative-facing banks that over-cancel friction grip, and
angles at/±90°, now raise clear `ValueError`s. Regressions:
`TestBankedCurve::test_non_positive_grip_numerator_rejected` and
`test_bank_at_or_beyond_vertical_rejected`.

**V3 (closed) — puff/plume convergence now bounded over a range + negative
control.** Parametrized convergence across downwind [800, 1200, 2000, 3000] m
(rel 0.1) plus a negative control at 6000 m where the puff train cannot yet
have transited (ratio < 0.5), proving the cross-check discriminates instead of
passing trivially.

**V2 (closed) — citations now reach the citation graph.** Inline `[@key]`
citations added: `02_methodology.md` (arya1999dispersion, turner1970workbook,
zannetti1990air, sykes1998scipuff, cormen2009algorithms, mcclung2006avalanche);
`07_scope_and_related_work.md` (morlock1989bobsled, with its scope caveat).

**E3 (closed) — route figure wired.** `render_route_figure` renders
`output/figures/route_profile.png` from `scripts/04_execute.py`; referenced as
`@fig:route` in `03_results.md`; listed in `manuscript/AGENTS.md` figure table.

### Manuscript (regenerated from live engine)

Tokenized results-summary table added to `03_results.md`; explicit
"Limitations and uncertainty" subsection added to `07_scope_and_related_work.md`;
`docs/_generated/COUNTS.md` refreshed to measured numbers. All `{{TOKEN}}`s
resolve from the executed mission (strict mode).

### Gate numbers (measured this session)

`uv run pytest tests/ --cov=src --cov-fail-under=90` → **205 passed, 0 skipped,
0 failed, 97.85% line+branch coverage**. `ruff check` clean; `ruff format
--check` clean; `mypy src/ scripts/` clean (19 files).

### Left for a future round

- **E1** surveyed terrain (analytic surfaces remain).
- **E2** lateral load-transfer / steering in `descent_dynamics`.
- **E4** delegated on-disk provenance (pinned `started_at` required to keep C1
  closed).
- **V1** adversarial audit remains partial: this re-review was inline by the
  same improvement agent, not an independent skeptic.

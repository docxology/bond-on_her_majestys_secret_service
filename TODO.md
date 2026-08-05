# TODO — on_her_majestys_secret_service (PIZ GLORIA)

Deterministic mission-software package for *On Her Majesty's Secret Service* (1969), modelling three
operational pillars: aerosol dispersion (steady Gaussian plume plus a Lagrangian puff train), alpine
descent (bobsleigh point-mass dynamics, curve physics, slope-safety-gated routing), and cover
identity (weighted persona risk plus interval-arithmetic timeline verification).

**Verified state, measured 2026-08-05:** `uv run pytest tests/ --cov=src --cov-fail-under=90` →
**192 passed, 98.13% coverage**. ruff, `ruff format --check` and mypy clean. Six domain modules plus
`mission.py` (frozen `bond_api.MissionProvider`) and `manuscript_variables.py`.

## Open work

### Correctness

**C1 — Regeneration is not byte-identical, but two manuscript sections say it is.**
`src/on_her_majestys_secret_service/manuscript_variables.py` derives `GENERATION_TIMESTAMP` from a
wall clock and renders it into persisted output, so every regeneration writes different bytes.
`manuscript/04_conclusion.md` and `manuscript/06_reproducibility.md` both claim byte-identical
reproduction. Confirmed empirically on 2026-08-05: two runs one second apart produced different
hashes.

*Done when:* the two-run hashes match, **or** every byte-identical claim is removed. Plus a
regeneration-determinism test that runs the generator twice and compares real bytes — a test that
injects a fixed `now` cannot detect this defect, which is why it survived. Prove the new test fails
by temporarily reintroducing the wall clock.

```bash
uv run python scripts/z_generate_manuscript_variables.py
find output -type f \( -name '*.json' -o -name '*.md' \) | sort | xargs cat | md5
sleep 1 && uv run python scripts/z_generate_manuscript_variables.py
find output -type f \( -name '*.json' -o -name '*.md' \) | sort | xargs cat | md5
```

This is a fleet-wide defect; 21 sibling packages carried it and were swept on 2026-08-05. **This
package was omitted from that sweep** and is the only one still carrying it.

### Verification

**V1 — This package has never been adversarially audited.** Every one of its 33 siblings was
attacked by an independent skeptic; three attempts on this package failed on model safeguards. Its
clean bill of health comes only from agents that were also improving it — precisely the arrangement
that produced overclaims elsewhere. Audit against the defect patterns actually found in siblings:

- **Green by construction** — a "recovered" value derived from the same quantity being recovered; a
  count that can only equal the number requested. Check every headline metric in
  `manuscript/03_results.md`: could it come out any other way?
- **Tautological controls** — a positive control asserting `X+1 != X`, never exercising the
  mechanism it advertises.
- **Figures bypassing canonical computation** — confirm `figures/` imports its numbers from the
  domain core rather than re-declaring constants. Editing `manuscript/config.yaml` must change the
  figures, not only the prose.
- **False mathematical claims in docstrings** — verify stated maths numerically against what the
  code computes. A sibling asserted a noncentrality parameter its own code contradicted, inflating a
  published probability from 54% to 66%.
- **Mis-attributed citations** — a sibling cited a real Haldane paper with the wrong year, volume
  and journal, *and* for a model it does not contain. Independently check each of the seven entries
  in `manuscript/references.bib` (Arya 1999, Turner 1970, Zannetti 1990, Sykes et al. 1998,
  Morlock & Zatsiorsky 1989, McClung & Schaerer 2006, Cormen et al. 2009): does the work exist with
  that year and venue, and does it contain the model it is cited for?
- **Hollow tests** — assertions that cannot fail, tests asserting only a return type or PNG magic
  bytes, substring assertions matching a label prefix regardless of the value.

*Done when:* an independent adversarial pass has run and its findings are recorded here or resolved.
This package repeatedly trips Opus safeguards; use a different model.

**V2 — The puff/plume convergence claim is asserted in prose.** `puff_dispersion.py` is documented
as provably converging to the steady plume far downwind.

*Done when:* the property is bound by a test with an explicit tolerance across a range of downwind
distances, plus a negative control at a distance where the two models should *not* agree.

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
cd /Users/4d/Documents/GitHub/template/projects/working/bond/on_her_majestys_secret_service

uv run pytest tests/ --cov=src --cov-fail-under=90   # expect 192 passed, ~98.13%
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/                            # expect clean, 19 files
```

Fleet-level gates run from the workspace root (`../`): `_phase_aggregate_gate.sh`,
`_phase_docs_gate.py`, `_phase_lint_sweep.sh`, `_phase_prerender_sweep.sh`. If `uv` reports
`Failed to initialize cache`, that is a sandbox restriction rather than a package failure — re-run
with the sandbox disabled.

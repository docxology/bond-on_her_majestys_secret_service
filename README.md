# on_her_majestys_secret_service — PIZ GLORIA

A PROJECT BOND film package drawn from **On Her Majesty's Secret Service**
(1969), mission codename **PIZ GLORIA**. It implements special-agent mission
software for an alpine operation: modeling the aerosol bioweapon (allergen)
dispersion threat, planning a bobsleigh-grade safe exfiltration route, and
scoring the *Bray* cover identity.

The package implements the frozen `bond_api` `MissionProvider` protocol and is
discoverable by any BOND coordinator by its slug
`on_her_majestys_secret_service`.

## What it does

Three pure, deterministic, infrastructure-free domain modules:

| Module | Concept | Method |
| --- | --- | --- |
| `dispersion_model.py` | Aerosol bioweapon (allergen) dispersion | Gaussian plume, Pasquill-Gifford stability, valley-channeled transport |
| `alpine_routes.py` | Alpine route planning (bobsleigh grade) | Track geometry + slope-safety-gated Dijkstra |
| `cover_identity.py` | Cover-identity risk (Bray persona) | Weighted additive risk scoring |

Plus the thin protocol adapter:

* `mission.py` — `MissionProvider` (brief / recon / plan / execute / debrief)
  with deterministic provenance and gadget registration.
* `manuscript_variables.py` — `{{TOKEN}}` hydration from config + live results.
* `figures/` — matplotlib rendering of the plume footprint and route profile.

## Layout

```
src/on_her_majestys_secret_service/   importable package (domain + mission)
scripts/                               thin mission-phase CLIs
tests/                                 real-data, mock-free test suite
manuscript/                            config + sections + layer contract
docs/                                  agent instructions, architecture, testing
```

## Install & verify

From this directory:

```bash
uv sync --extra dev
uv run python -m pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

Run the mission phases:

```bash
uv run python scripts/01_brief.py      # mission definition
uv run python scripts/02_recon.py      # recon findings
uv run python scripts/03_plan.py       # execution plan
uv run python scripts/04_execute.py    # run + write outcome/figure
uv run python scripts/05_debrief.py    # lessons
uv run python scripts/z_generate_manuscript_variables.py   # hydrate tokens
```

This is a **local-only** BOND working tree: there is no remote, and nothing
here is pushed.

## Integration

The `MissionProvider` in `mission.py` satisfies the frozen `bond_api`
protocol; `bond_api.discovery.load_provider("on_her_majestys_secret_service")`
resolves it for coordinators. Gadgets (the dispersion scenario, the plume
isopleth, the alpine planner, the cover risk scorer) register into a
`GadgetRegistry` on import.

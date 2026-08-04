# Architecture — PIZ GLORIA

## Layering

```
scripts/ (thin CLIs)
   |
   v
src/on_her_majestys_secret_service/mission.py   (bond_api MissionProvider adapter)
   |                 \
   |                  +-- manuscript_variables.py (token hydration)
   |                  +-- figures/ (matplotlib rendering)
   v
pure domain core
   dispersion_model.py   Gaussian plume + valley channeling
   alpine_routes.py      track geometry + slope-safe Dijkstra
   cover_identity.py     weighted cover-risk scoring
```

## Dependency direction

* **Domain core** imports only stdlib (+ nothing else): no `bond_api`, no
  `infrastructure`, no I/O. This is the standalone fallback — if the `bond-api`
  path dependency ever fails, the pure science still imports and runs.
* **`mission.py`** imports `bond_api.protocol`, `bond_api.registry`, and the
  three domain modules. It is the only place the film binds to the protocol.
* **`manuscript_variables.py`** imports `mission.run_scenario` + `yaml` +
  `numpy` and produces `{{TOKEN}}` values.
* **`figures/`** imports the domain modules and matplotlib; deterministic,
  headless (Agg).
* **`scripts/`** bootstrap `sys.path` to `src/` and invoke `src/`.

## Determinism

* `mission.SCENARIO` is a fixed `PlumeScenario`; the seed is fixed (`7`).
* `run_scenario()` is a pure function of the fixed scenario → identical output.
* Provenance `input_hash` is a SHA-256 over the sorted scenario inputs.
* No wall-clock time enters any persisted artifact (`wall_time_s = 0.0`).

## Identity

* Film: On Her Majesty's Secret Service (1969).
* Mission codename: PIZ GLORIA.
* Protocol slug: `on_her_majestys_secret_service`.
* Provider: `src/on_her_majestys_secret_service/mission.py::MissionProvider`.

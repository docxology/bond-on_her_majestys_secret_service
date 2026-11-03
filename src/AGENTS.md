# src/ — pure domain core, adapter, derived surface

Six pure domain modules (`dispersion_model.py`, `puff_dispersion.py`, `alpine_routes.py`,
`descent_dynamics.py`, `cover_identity.py`, `identity_timeline.py`), the `mission.py`
adapter, the derived layer (`manuscript_variables.py`, `figures/`) and `__init__.py`.

## Rules

- **Keep the layer contract.** The domain modules are pure: no I/O, no `bond_api`, no
  infrastructure imports, importable standalone. Only `mission.py` and its downstream layers
  may touch `bond_api`, so a failure of the path dependency never blocks the pure science.
- **Protocol stability.** The discovery surface is frozen: the `film` value, the five
  `MissionProvider` methods (`brief`, `recon`, `plan`, `execute`, `debrief`), the
  `register_gadgets` hook and the module-level `REGISTRY`. Deepen inside the package, never in
  the discovery contract.
- **Treat the domain maths seriously** — gas dispersion, slope safety and descent kinetics,
  weighted risk and timeline verification are real science, and the code should read that way.
- **Deterministic.** Fixed seeds; `run_scenario()` must return byte-identical results across
  runs; no wall-clock time in a persisted artifact.
- No mocks in `src/`; coverage floor 90% line and branch on `src/`.

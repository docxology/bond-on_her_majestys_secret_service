# Experimental setup {#sec:experimental_setup}

## Scenario parameters

The PIZ GLORIA release and routing scenario is fixed in
`src/on_her_majestys_secret_service/mission.py` and mirrored in
`manuscript/config.yaml`:

* Release rate: `0.05` kg/s aerosolised allergen.
* Free-stream wind speed: `4.0` m/s (inferred stability class `C`, slightly unstable).
* Effective release height: `25.0` m.
* Valley channeling depth: `400.0` m, floor wind ratio `0.6`.
* High-hazard isopleth threshold: `1.0e-7` kg/m^3.
* Route grid: `40 x 40` cells over a 10 km x 10 km analytic range,
  maximum safe slope `30` deg.

## Software environment

* Package: `on_her_majestys_secret_service` {{BOND_VERSION}}
* Python: {{PYTHON_VERSION}}
* NumPy: {{NUMPY_VERSION}}
* Protocol: `bond_api` (frozen MissionProvider contract)
* Manuscript variables generated: {{GENERATION_TIMESTAMP}} (UTC)

## Guarantees

Every result value is produced by the executed mission and injected through the
manuscript-variable pipeline; none is hand-written into prose.

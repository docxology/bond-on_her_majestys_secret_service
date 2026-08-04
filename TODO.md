# TODO — on_her_majestys_secret_service (PIZ GLORIA)

## Built (phase-2)

* `src/on_her_majestys_secret_service/dispersion_model.py` — Gaussian-plume
  aerosol dispersion with Pasquill-Gifford stability coefficients and
  valley-channeled transport. Exposed: `pasquill_sigma`, `PlumeScenario`,
  `point_concentration`, `centerline_concentration`,
  `peak_ground_concentration`, `downwind_axis`, `isopleth_distance`,
  `inhalation_dose`, `valley_wind_factor`, `stability_class`.
* `src/on_her_majestys_secret_service/alpine_routes.py` — bobsleigh-grade
  track geometry (slope, chord length, Menger curvature), segment safety
  classification, route safety report, and a slope-safety-gated Dijkstra
  planner (`plan_safe_route`) on an analytic alpine surface.
* `src/on_her_majestys_secret_service/cover_identity.py` — weighted
  cover-identity risk scoring for the Bray persona (`attribute_risk`,
  `cover_score`, `risk_verdict`, `breach_scenario`, `bray_persona`).
* `src/on_her_majestys_secret_service/mission.py` — `MissionProvider` adapter
  implementing the frozen `bond_api` protocol (brief/recon/plan/execute/
  debrief) with deterministic provenance, plus gadget registration.
* `src/on_her_majestys_secret_service/manuscript_variables.py` — `{{TOKEN}}`
  hydration from `manuscript/config.yaml` + live mission results.
* `src/on_her_majestys_secret_service/figures/` — dispersion plume footprint
  and route elevation-profile figures (matplotlib, Agg).
* `scripts/` — `00_preflight.py`, `01_brief.py` .. `05_debrief.py`,
  `z_generate_manuscript_variables.py`.
* `tests/` — per-concept real-data suites + mission/discovery/protocol,
  manuscript-token live cross-reference gate, figures, and script smoke tests.
  >=90% line+branch coverage on `src/` enforced.

## Integration points (declared)

1. **`bond-api` protocol**: the `MissionProvider` in `mission.py` is built
   against the frozen `bond_api` types and registered via `[tool.uv.sources]`
   path dependency. No further work expected — contract is frozen.
2. **Gadget registry**: the film registers four gadgets
   (`dispersion_model`, `plume_footprint`, `alpine_planner`, `cover_risk`)
   into a `bond_api.GadgetRegistry`; wire these into a coordinator's
   gadget inventory when the coordinator is ready.
3. **Provenance persistence**: outcomes currently carry `Provenance` in-memory;
   once `bond_utilities.mission_io.record_provenance_outcome` is available to
   downstream packages, `scripts/04_execute.py` can delegate the on-disk
   record to it (acceptance: a deterministic JSON/YAML record keyed by the
   input hash).
4. **Surveyed terrain**: `alpine_routes` plans on an analytic test surface;
   swap the `elevation_func` for a surveyed elevation raster to move from
   illustrative to operational routing.

## Follow-ups

* Consider a `render_route_figure` integration into `scripts/04_execute.py`.
* Bump the manuscript's figure registry when a route figure is added.

# Scope and related work {#sec:scope}

## Scope

The PIZ GLORIA software is illustrative mission engineering, not a certified
hazard-assessment tool, and its claims are bounded accordingly:

* **Dispersion** — the steady-state Gaussian plume is a screening model: it
  assumes a continuous release, uniform wind, and flat-terrain reflection. It
  does not model time-varying release, terrain-following plumes, chemical
  transformation, or deposition. The valley correction is a scalar channeling
  factor, not a 3-D CFD solution.
* **Routing** — the planner operates on an analytic test surface, not surveyed
  terrain, and its 8-connected grid over-approximates feasible continuous
  paths. Real operational routing would ingest surveyed elevation rasters and
  add kinematic bobsleigh constraints.
* **Cover identity** — the weighted risk score is a defensible decision aid but
  depends on the analyst's choice of weights and the normalization of evidence;
  it is not a calibrated probability.

## Related work

Gaussian plume dispersion follows the classical Pasquill-Gifford formulation
(e.g. Arya, *Air Pollution Meteorology and Dispersion*, 1999) with the standard
open-country stability coefficient set. Alpine slope-safety routing draws on
standard terrain-aware path planning (Dijkstra over elevation grids with grade
gates), and additive weighted risk scoring parallels common threat-assessment
frameworks. Where a precise field value matters, the open-country dispersion
coefficients are the fixed, cited data table in `dispersion_model.py`.

# Scope and related work {#sec:scope}

## Scope

The PIZ GLORIA software is illustrative mission engineering, not a certified
hazard-assessment tool, and its claims are bounded accordingly:

* **Dispersion** — the steady-state Gaussian plume and its puff-train variant
  are screening models: they assume a continuous release, uniform wind, and
  flat-terrain reflection, and do not model time-varying release composition,
  terrain-following plumes, chemical transformation, or deposition.
* **Descent dynamics** — the point-mass integration is a planar 1-D model:
  no steering, no lateral load transfer into the friction model, and a single
  scalar drag coefficient. The canonical track is analytic, not surveyed.
* **Routing** — the planner operates on an analytic test surface, not surveyed
  terrain, and its 8-connected grid over-approximates feasible continuous
  paths.
* **Cover identity / timeline** — the weighted risk score and interval
  coverage depend on analyst-chosen weights, evidence normalization, and the
  observation set; they are decision aids, not calibrated probabilities.

## Related work

Gaussian plume/puff dispersion follows the classical Pasquill-Gifford
formulation (Arya 1999; Turner 1970) and the Lagrangian puff-train approach
used by operational puff models (Zannetti 1990; Sykes et al. 1998). Point-mass
descent with friction and drag draws on bobsleigh biomechanics literature
(Morlock & Zatsiorsky 1989), and alpine slope/avalanche safety rating follows
the standard danger-scale practice (McClung & Schaerer 2006). Interval-based
timeline verification uses standard interval arithmetic / coverage analysis.
Where a precise field value matters, the open-country dispersion coefficients
are the fixed, cited data tables in `dispersion_model.py`.

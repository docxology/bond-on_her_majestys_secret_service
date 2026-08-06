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

## Limitations and uncertainty

Beyond the scope boundaries above, the headline numbers carry specific,
unquantified uncertainties that a user should read alongside them:

* **Dispersion coefficients** are the fixed open-country Pasquill-Gifford
  tables, which are screening values, not site-calibrated measurements. The
  isopleth reach and peak location therefore inherit ± a factor of several in
  absolute hazard extent under real alpine meteorology.
* **Valley-channeling** enters as a single scalar floor factor; real
  topography funnels wind non-uniformly, so ground-level concentrations are
  order-of-magnitude estimates.
* **Puff timing** depends on the discrete emission cadence $\Delta t$ and
  initial puff size: the arrival time is accurate to within roughly one
  cadence (10 s) and the transient peak is resolution-dependent.
* **Descent dynamics** are a single-degree-of-freedom point mass with no
  steering or lateral load transfer; the reported speeds and g-loads bound the
  physics but are not a certified vehicle- or rider-specific prediction.
* **Route geometry** is analytic, and the reported distance/grade are
  properties of that surface, not measured survey data.
* **Cover metrics** depend on analyst-chosen weights, evidence normalization,
  and the observation set; they are decision aids with no calibrated
  probability semantics.

These are stated so no headline number is read as a measurement of the world:
each is a deterministic property of the stated model and its fixed inputs.

## Related work

Gaussian plume/puff dispersion follows the classical Pasquill-Gifford
formulation (Arya 1999; Turner 1970) and the Lagrangian puff-train approach
used by operational puff models (Zannetti 1990; Sykes et al. 1998). Point-mass
descent with friction and drag draws on bobsleigh performance framing
[@morlock1989bobsled] (whose scope is strictly the regression in
`99_references.md`; it does not underwrite the rigid-body equations), and alpine slope/avalanche safety rating follows
the standard danger-scale practice (McClung & Schaerer 2006). Interval-based
timeline verification uses standard interval arithmetic / coverage analysis.
Where a precise field value matters, the open-country dispersion coefficients
are the fixed, cited data tables in `dispersion_model.py`.

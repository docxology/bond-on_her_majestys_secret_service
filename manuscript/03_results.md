# Results {#sec:results}

The executed PIZ GLORIA mission produces three deterministic result groups.

## Dispersion footprint

At the configured release (see @sec:experimental_setup) the model locates a
peak ground-level centreline concentration of **{{PIZ_PEAK_CONCENTRATION}}** at
**{{PIZ_PEAK_DISTANCE_M}}** downwind. The high-hazard isopleth (ground-level
concentration at or above the configured threshold) reaches
**{{PIZ_ISOPLETH_REACH_M}}** down-valley — the far edge of the exposure band,
driven by the elevated release and valley-channeled transport.

![Ground-level centreline aerosol concentration along the plume axis.](../output/figures/aerosol_plume.png){#fig:dispersion}

The footprint is summarized by the computed upwind dispersion class from the
scenario and displayed in @fig:dispersion on a log concentration axis.

## Alpine exfiltration route

The slope-safety-gated planner returns a **{{PIZ_ROUTE_SAFE}}** route of
**{{PIZ_ROUTE_DISTANCE_M}}** with a mean grade of **{{PIZ_ROUTE_MEAN_GRADE_DEG}}**.
Every step of the reconstructed line respects the declared maximum slope gate;
the planner's cost objective (distance plus grade penalty) yields the shortest
safe track under its metric across the analytic alpine test surface.

## Cover identity

The canonical *Bray* persona scores **{{PIZ_BRAY_SCORE}}**
(**{{PIZ_BRAY_VERDICT}}** risk). The dominant exposure driver is forensic
overlap; under a full forensic breach the aggregate score rises and the verdict
escalates, demonstrating that the alias is defensible only while that evidence
stays low.

# Results {#sec:results}

The executed PIZ GLORIA mission produces six deterministic result groups.

## Dispersion footprint

At the configured release (see @sec:experimental_setup) the model locates a
peak ground-level centreline concentration of **{{PIZ_PEAK_CONCENTRATION}}** at
**{{PIZ_PEAK_DISTANCE_M}}** downwind. The high-hazard isopleth (ground-level
concentration at or above the configured threshold) reaches
**{{PIZ_ISOPLETH_REACH_M}}** down-valley — the far edge of the exposure band,
driven by the elevated release and valley-channeled transport.

![Ground-level centreline aerosol concentration along the plume axis.](../output/figures/aerosol_plume.png){#fig:dispersion}

## Puff arrival and early warning

At the downstream receptor the Lagrangian puff train shows the allergen first
crosses the detection threshold after **{{PIZ_PUFF_ARRIVAL_S}}**, with a
transient peak of **{{PIZ_PUFF_PEAK_CONC}}**. This is the operational
early-warning lead: the steady plume describes the average threat, but the puff
dynamics give the time at which a sensor would first alarm.

![Puff concentration time series at the downstream receptor.](../output/figures/puff_footprint.png){#fig:puff}

## Alpine exfiltration route

The slope-safety-gated planner returns a **{{PIZ_ROUTE_SAFE}}** route of
**{{PIZ_ROUTE_DISTANCE_M}}** with a mean grade of **{{PIZ_ROUTE_MEAN_GRADE_DEG}}**.
Every step of the reconstructed line respects the declared maximum slope gate.

## Bobsleigh descent and banked-curve clearance

Point-mass kinematics over the canonical bobsleigh track complete the descent
in **{{PIZ_DESCENT_TIME_S}}**, peaking at **{{PIZ_DESCENT_MAX_SPEED_M_S}}**
(Figure @fig:descent). The unbanked canonical hairpin carries
**{{PIZ_TRACK_MAX_G}}** of lateral load — **{{PIZ_TRACK_SAFE}}** the 4-g
ceiling — so the line must be banked; a 55-degree bank raises the safe cornering
speed to **{{PIZ_BANKED_MAX_SPEED_M_S}}**.

![Bobsleigh descent speed profile along the canonical track.](../output/figures/descent_profile.png){#fig:descent}

## Cover identity

The canonical *Bray* persona scores **{{PIZ_BRAY_SCORE}}**
(**{{PIZ_BRAY_VERDICT}}** risk); the dominant exposure driver is forensic
overlap.

## Timeline verification

Auditing the persona's claimed timeline against four sightings yields a
**{{PIZ_TIMELINE_VERDICT}}** verdict at **{{PIZ_TIMELINE_COVERAGE}}** coverage
with **{{PIZ_TIMELINE_CONFLICTS}}** contradiction(s): a London sighting that
contradicts the Piz Gloria claim. One contradicting observation is enough to
unseat an otherwise-covered story — the cover holds only while the timeline is
unbroken.

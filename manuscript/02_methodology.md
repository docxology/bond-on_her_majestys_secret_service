# Methodology {#sec:methodology}

## Aerosol bioweapon dispersion

The dispersion core models a continuous, elevated release of an aerosolized
allergen bioweapon transported downwind by the mean wind. We use the
steady-state Gaussian plume solution for a point source with ground reflection:

$$C(x,y,z) = \frac{Q}{2\pi u\,\sigma_y\,\sigma_z}
  \exp\!\left(-\frac{y^2}{2\sigma_y^2}\right)
  \left[\exp\!\left(-\frac{(z-H)^2}{2\sigma_z^2}\right)
        +\exp\!\left(-\frac{(z+H)^2}{2\sigma_z^2}\right)\right]$$

where $Q$ is the release rate [kg/s], $u$ the effective transport wind [m/s],
$H$ the effective release height [m], and $\sigma_y,\sigma_z$ the horizontal and
vertical dispersion coefficients. The coefficients follow the open-country
Pasquill-Gifford power laws $\sigma_y = a x^b$ and $\sigma_z = c x^d$, with the
standard per-stability-class coefficient set (classes A–F, unstable to
stable).

Because the release sits in a valley, the transport wind is corrected by a
channeling factor

$$f(e) = 1 - (1 - f_0)\,\exp(-e / d_v),$$

which slows the plume most at the valley floor ($f_0$ is the floor wind ratio)
and returns toward free-stream flow with increasing receptor elevation $e$
relative to the valley depth $d_v$. The far edge of the ground-level isopleth
at a fixed concentration threshold is computed by a coarse scan plus
bisection refinement, giving the mission's reach metric.

## Alpine route planning

A planned track is a polyline of waypoints in projected coordinates
(easting, northing, elevation). Three geometry quantities govern a
bobsleigh-grade line:

* chord slope: $\theta = \arctan(|\Delta z| / \sqrt{\Delta e^2 + \Delta n^2})$,
* 3-D chord length for cumulative distance,
* discrete Menger curvature $k = 4A / (|ab|\,|bc|\,|ca|)$ for turn sharpness.

A segment is classified *safe*, *marginal*, or *unsafe* by grade and rejected
when it also violates a curvature cap; the planner runs Dijkstra on an
8-connected grid, discarding any step whose chord grade exceeds the maximum
safe slope, and costs the remainder by distance plus a grade penalty.

## Cover-identity risk scoring

Each identity attribute $a$ carries a weight $w_a$ and a risk $r_a\in[0,1]$.
The aggregate cover risk is the weighted mean $\sum w_a r_a / \sum w_a$, and an
attribute risk is a linear function $r_a = \beta_a + m_a\,c_a$ of normalized
incriminating evidence $c_a$. A breach scenario raises one or more attributes'
evidence and recomputes the aggregate and its discrete verdict.

## Time-dependent puff dispersion

To capture *when* a threat arrives, the continuous release is discretized into
a deterministic train of Gaussian puffs. Puff $i$, emitted at $t_i$ with mass
$Q\,\Delta t$, advects downwind at the effective wind and spreads as it
travels. Superimposing every emitted puff at a receptor gives a concentration
time series, whose early crossing of a detection threshold is the **arrival
time** — the operational early-warning metric. For a steady release the puff
superposition converges to the plume solution far downwind, a cross-check the
tests assert directly.

## Bobsleigh descent dynamics

A point-mass slides under gravity down a track profile resisted by kinetic
friction and aerodynamic drag:

$$a(v) = g\sin\theta - \mu g\cos\theta - k v^2, \qquad k = \tfrac{1}{2}\rho C_d A / m,$$

integrated with a fixed time step along the polyline. Because a bobsleigh line
is defined by its turns, the module pairs the speed profile with curve physics:
lateral g-load $v^2/(gR)$ and the banked-curve speed limit
$v_{\max} = \sqrt{gR\,(\tan\beta + \mu_L)/(1 - \mu_L \tan\beta)}$.

## Cover-timeline verification

A cover is as strong as its timeline. Claimed events and observed sightings
are intervals $[s, e)$ over mission minutes; an observation is *matched* when an
overlapping claim agrees on location and *conflicts* when an overlapping claim
names a different location. The coverage fraction (matched observed minutes
over total observed minutes) yields a discrete verdict, and a single
contradicting sighting can unseat an otherwise-covered story.

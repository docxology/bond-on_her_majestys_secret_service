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

"""Aerosol bioweapon (allergen) dispersion modeling — PIZ GLORIA.

This module implements the deterministic core of the PIZ GLORIA mission's
primary deliverable: modeling the atmospheric dispersion of an aerosolized
allergen bioweapon released at an alpine source and transported downwind
through a valley.

The model is the classical **steady-state Gaussian plume** for a continuous
point source with ground reflection:

    C(x, y, z) = Q/(2*pi*u*sig_y*sig_z) * exp(-y^2 / (2 sig_y^2))
                * [ exp(-(z-H)^2 / (2 sig_z^2)) + exp(-(z+H)^2 / (2 sig_z^2)) ]

where ``Q`` [kg/s] is the release rate, ``u`` [m/s] the mean wind speed, ``H``
[m] the effective release height, ``(x, y, z)`` the downwind / crosswind /
vertical coordinates, and ``sig_y(sig_z)`` the horizontal (vertical) dispersion
coefficients.

Vertical and crosswind spread follow a Pasquill-Gifford power law in downwind
distance ``x`` derived from observed stability data (the standard open-country
coefficient set, see :data:`PG_OPEN_COUNTRY_Y` / :data:`PG_OPEN_COUNTRY_Z`,
after Arya 1999). Stability classes ``A``..``F`` move from unstable (A, fast
vertical mixing) to stable (F, suppressed vertical mixing).

Valley transport modifies the effective wind speed by a valley-channeling
factor (:func:`valley_wind_factor`), modelling topographic funneling of the
plume along a valley axis.

All math is deterministic and side-effect free: no random draws, no wall-clock,
no I/O. Everything downstream (mission execution, figures, manuscript tokens)
derives from these functions.
"""

from __future__ import annotations

import math
from typing import Final

__all__ = [
    "PG_OPEN_COUNTRY_Y",
    "PG_OPEN_COUNTRY_Z",
    "PlumeScenario",
    "centerline_concentration",
    "downwind_axis",
    "ground_level_concentration",
    "inhalation_dose",
    "isopleth_distance",
    "pasquill_sigma",
    "peak_ground_concentration",
    "point_concentration",
    "stability_class",
    "valley_wind_factor",
]

#: Pasquill-Gifford sigma-y power-law coefficients ``(a, b)`` for
#: ``sig_y = a * x**b``, open country, ``x`` in metres. Classes A..F from
#: unstable to stable. Standard set (see module docstring / Arya 1999).
PG_OPEN_COUNTRY_Y: Final[dict[str, tuple[float, float]]] = {
    "A": (0.22, 0.894),
    "B": (0.16, 0.894),
    "C": (0.11, 0.894),
    "D": (0.08, 0.894),
    "E": (0.06, 0.894),
    "F": (0.04, 0.894),
}

#: Pasquill-Gifford sigma-z power-law coefficients ``(c, d)`` for
#: ``sig_z = c * x**d``, open country, ``x`` in metres.
PG_OPEN_COUNTRY_Z: Final[dict[str, tuple[float, float]]] = {
    "A": (0.20, 1.00),
    "B": (0.12, 0.91),
    "C": (0.08, 0.82),
    "D": (0.06, 0.71),
    "E": (0.03, 0.67),
    "F": (0.02, 0.55),
}


def _validate_stability(stability: str) -> None:
    if stability not in PG_OPEN_COUNTRY_Y:
        raise ValueError(
            f"unknown stability class {stability!r}; expected one of {list(PG_OPEN_COUNTRY_Y)}"
        )


def pasquill_sigma(x: float, stability: str) -> tuple[float, float]:
    """Return ``(sigma_y, sigma_z)`` Pasquill-Gifford dispersion coefficients.

    Args:
        x: Downwind distance from the source in metres (must be >= 0).
        stability: Pasquill stability class ``'A'``..``'F'``.

    Returns:
        ``(sigma_y, sigma_z)`` in metres, from the open-country power laws.

    Raises:
        ValueError: if ``x < 0`` or ``stability`` is not a known class.
    """
    if x < 0:
        raise ValueError(f"downwind distance must be >= 0, got {x}")
    _validate_stability(stability)
    ay, by = PG_OPEN_COUNTRY_Y[stability]
    cz, dz = PG_OPEN_COUNTRY_Z[stability]
    return ay * x**by, cz * x**dz


class PlumeScenario:
    """A deterministic release scenario: source, meteorology, dispersion.

    Attributes:
        release_rate: ``Q`` release rate of the aerosol bioweapon [kg/s].
        wind_speed: free-stream ``u`` mean wind speed [m/s].
        release_height: effective ``H`` release height [m].
        stability: Pasquill stability class.
        valley: height of surrounding terrain invoked for valley channeling
            (or ``None`` to disable); drives :func:`valley_wind_factor`.
    """

    def __init__(
        self,
        release_rate: float,
        wind_speed: float,
        release_height: float = 10.0,
        stability: str = "D",
        valley: float | None = None,
    ) -> None:
        if release_rate < 0:
            raise ValueError(f"release_rate must be >= 0, got {release_rate}")
        if wind_speed <= 0:
            raise ValueError(f"wind_speed must be > 0, got {wind_speed}")
        if release_height < 0:
            raise ValueError(f"release_height must be >= 0, got {release_height}")
        _validate_stability(stability)
        self.release_rate = float(release_rate)
        self.wind_speed = float(wind_speed)
        self.release_height = float(release_height)
        self.stability = stability
        self.valley = float(valley) if valley is not None else None

    def effective_wind_speed(self, elevation: float = 0.0) -> float:
        """Return the wind speed used for transport, adjusted for a valley.

        When a valley is configured, channeling multiplies the free-stream wind
        by :func:`valley_wind_factor`, which rises toward ``1`` with increasing
        ``elevation`` above the valley floor (topographic funneling weakens as
        the plume escapes the trough). No valley -> the free-stream speed.
        """
        if self.valley is None:
            return self.wind_speed
        return self.wind_speed * valley_wind_factor(elevation, self.valley)


def valley_wind_factor(
    elevation: float, valley_depth: float, floor_factor: float = 0.6
) -> float:
    """Valley-channeling factor in ``(0, 1]`` for a given elevation.

    Channeling slows the wind most at the valley floor (factor ``floor_factor``)
    and decays exponentially toward 1 as elevation rises relative to
    ``valley_depth``:

        f = 1 - (1 - floor_factor) * exp(-elevation / valley_depth)

    The factor never reaches 0, so the Gaussian plume always has a nonzero
    transport speed. ``floor_factor`` in ``(0, 1]`` sets the floor wind ratio.

    Args:
        elevation: height above the valley floor [m].
        valley_depth: characteristic channeling scale (valley depth) [m].
        floor_factor: wind-speed ratio at the valley floor, in ``(0, 1]``.
    """
    if valley_depth <= 0:
        raise ValueError(f"valley_depth must be > 0, got {valley_depth}")
    if elevation < 0:
        raise ValueError(f"elevation must be >= 0, got {elevation}")
    if not (0.0 < floor_factor <= 1.0):
        raise ValueError(f"floor_factor must be in (0, 1], got {floor_factor}")
    return 1.0 - (1.0 - floor_factor) * math.exp(-elevation / valley_depth)


def point_concentration(
    x: float,
    y: float,
    z: float,
    scenario: PlumeScenario,
    *,
    elevation: float = 0.0,
) -> float:
    """Gaussian plume concentration ``C(x, y, z)`` [kg/m^3] at one point.

    Includes an image-source ground-reflection term and a valley-channeling
    adjustment to the effective wind speed.

    Args:
        x: downwind distance [m] (>= 0).
        y: crosswind offset [m].
        z: receptor height above ground [m].
        scenario: the release scenario.
        elevation: receptor elevation above the valley floor for channeling.
    """
    if x < 0:
        raise ValueError(f"downwind distance must be >= 0, got {x}")
    if z < 0:
        raise ValueError(f"receptor height must be >= 0, got {z}")
    sigma_y, sigma_z = pasquill_sigma(x, scenario.stability)
    u = scenario.effective_wind_speed(elevation)
    q = scenario.release_rate
    h = scenario.release_height
    if q == 0 or sigma_y * sigma_z * u == 0:
        return 0.0
    term_y = math.exp(-(y * y) / (2.0 * sigma_y * sigma_y))
    term_z = math.exp(-((z - h) ** 2) / (2.0 * sigma_z * sigma_z)) + math.exp(
        -((z + h) ** 2) / (2.0 * sigma_z * sigma_z)
    )
    return q / (2.0 * math.pi * u * sigma_y * sigma_z) * term_y * term_z


def centerline_concentration(
    x: float, scenario: PlumeScenario, *, elevation: float = 0.0
) -> float:
    """Downwind centerline concentration at ground level (y=0, z=0)."""
    return point_concentration(x, 0.0, 0.0, scenario, elevation=elevation)


def ground_level_concentration(
    x: float,
    y: float,
    scenario: PlumeScenario,
    *,
    receptor_height: float = 1.5,
    elevation: float = 0.0,
) -> float:
    """Ground-level concentration at a breathing height receptor."""
    return point_concentration(x, y, receptor_height, scenario, elevation=elevation)


def peak_ground_concentration(scenario: PlumeScenario) -> tuple[float, float]:
    """Ground-level centerline peak: ``(downwind distance [m], concentration
    [kg/m^3])`` where the ground-level centerline concentration is maximized.

    A line search over ``x`` locates the maximum of the centerline profile;
    for an elevated source the peak lies where vertical spread ``sig_z`` is on
    the order of the release height. Returns a deterministic result.
    """
    # Brute-force scan over a fine grid followed by one parabolic refinement.
    best_x, best_c = 0.0, 0.0
    samples = 2000
    for i in range(samples + 1):
        x = 5.0 + i * (5000.0 / samples)
        c = centerline_concentration(x, scenario)
        if c > best_c:
            best_c, best_x = c, x
    if best_x <= 5.0 or best_x >= 5005.0:
        return best_x, best_c
    # One-point parabolic refinement around the discrete max.
    x0, x1, x2 = best_x - 2.5, best_x, best_x + 2.5
    c0, c1, c2 = (
        centerline_concentration(x0, scenario),
        centerline_concentration(x1, scenario),
        centerline_concentration(x2, scenario),
    )
    denom = 2.0 * (c0 - 2.0 * c1 + c2)
    if abs(denom) > 1e-30:
        refined = x1 - (c2 - c0) / denom * 2.5
        if 0 < refined < 10000:
            best_x, best_c = refined, centerline_concentration(refined, scenario)
    return best_x, best_c


def downwind_axis(
    x_start: float,
    x_end: float,
    steps: int,
    scenario: PlumeScenario,
    *,
    elevation: float = 0.0,
) -> dict[str, list[float]]:
    """Centerline concentration profile along the plume axis.

    Returns a deterministically generated CSV-shaped mapping suitable for
    plotting/figures and manuscript data tokens: ``distance`` and
    ``concentration`` lists.
    """
    if steps <= 0:
        raise ValueError(f"steps must be > 0, got {steps}")
    distances = [x_start + (x_end - x_start) * i / steps for i in range(steps + 1)]
    concentrations = [
        centerline_concentration(x, scenario, elevation=elevation) for x in distances
    ]
    return {"distance": distances, "concentration": concentrations}


def isopleth_distance(
    threshold: float,
    scenario: PlumeScenario,
    *,
    max_distance: float = 20000.0,
    elevation: float = 0.0,
) -> float:
    """Farthest downwind reach [m] where the ground centerline concentration
    still equals/exceeds ``threshold`` [kg/m^3] — the far edge of a hazard band.

    For an elevated release the ground concentration is near-zero directly
    under the stack (the plume has not yet spread down to the surface), rises
    to a peak, then decays: the isopleth is therefore a contiguous band and the
    meaningful reach is its *farthest* extent. Returns ``0.0`` when the
    threshold is never reached within the scan window.

    Args:
        threshold: target concentration [kg/m^3].
        scenario: release scenario.
        max_distance: upper bound of the search window [m].
        elevation: elevation for valley-channeling.
    """
    if threshold < 0:
        raise ValueError(f"threshold must be >= 0, got {threshold}")
    if max_distance <= 0:
        raise ValueError(f"max_distance must be > 0, got {max_distance}")
    step = max_distance / 2000.0
    last = 0.0
    reached = False
    for i in range(1, 2000 + 1):
        x = i * step
        if centerline_concentration(x, scenario, elevation=elevation) >= threshold:
            last = x
            reached = True
    if not reached:
        return 0.0
    if last >= max_distance - 1e-9:
        return max_distance
    # Refine around the far edge (last above-threshold, last+step below).
    lo, hi = last, last + step
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if centerline_concentration(mid, scenario, elevation=elevation) >= threshold:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def inhalation_dose(
    concentration: float,
    exposure_time: float,
    breathing_rate: float = 1.25e-5,
) -> float:
    """Cumulative inhaled mass of aerosol [kg] over an exposure.

    ``dose = C * Q_breath * t`` where ``Q_breath`` is a resting breathing rate
    in m^3/s (default 20 l/min ≈ 3.33e-4 m^3/s is breathing; here the default
    1.25e-5 m^3/s models a low minute-volume filter scenario — callers should
    pass a realistic minute volume). Units are consistent with ``C`` in kg/m^3.
    """
    if concentration < 0:
        raise ValueError(f"concentration must be >= 0, got {concentration}")
    if exposure_time < 0:
        raise ValueError(f"exposure_time must be >= 0, got {exposure_time}")
    if breathing_rate <= 0:
        raise ValueError(f"breathing_rate must be > 0, got {breathing_rate}")
    return concentration * breathing_rate * exposure_time


def stability_class(wind_speed: float, *, daytime: bool = True) -> str:
    """Infer a Pasquill stability class from wind speed and insolation.

    A simplified, deterministic pass over the conventional daytime/night-time
    stability categories (used to seed a scenario when the class is not
    observed directly). Daytime with light wind -> unstable ``A``; strong wind
    -> neutral ``D``; clear night, light wind -> stable ``F``.

    Args:
        wind_speed: mean wind speed at 10 m [m/s].
        daytime: True for daytime (insolation) conditions.

    Returns:
        A Pasquill-Gifford stability class in ``A``..``F``.
    """
    if wind_speed < 0:
        raise ValueError(f"wind_speed must be >= 0, got {wind_speed}")
    if daytime:
        if wind_speed < 2:
            return "A"
        if wind_speed < 3:
            return "B"
        if wind_speed < 5:
            return "C"
        if wind_speed < 7:
            return "D"
        return "D"
    if wind_speed < 2:
        return "F"
    if wind_speed < 3:
        return "E"
    if wind_speed < 5:
        return "D"
    return "D"

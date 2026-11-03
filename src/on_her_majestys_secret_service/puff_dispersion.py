"""Lagrangian Gaussian puff dispersion — temporal dynamics of an aerosol release.

The steady-state plume (``dispersion_model``) answers *where the average threat
is*; PIZ GLORIA also needs *when it arrives*. This module models a continuous
release as a deterministic train of Gaussian puffs: each puff carries a fixed
mass ``Q * dt``, is released at a regular interval, advects downwind at the
effective transport wind, and spreads as it travels. Superimposing every
emitted puff at a downwind receptor gives a concentration **time series** —

    C(x_r, t) = sum_i Q_i / ((2 pi)^{3/2} sigma_x sigma_y sigma_z)
                * exp(-(x_r - x_i(t))^2 / (2 sigma_x^2))
                * exp(-y_r^2 / (2 sigma_y^2))
                * [ exp(-(z_r - H)^2 / (2 sigma_z^2))
                  + exp(-(z_r + H)^2 / (2 sigma_z^2)) ]

where puff ``i`` released at ``t_i`` has mass ``Q dt`` and centreline
downwind position ``x_i(t) = u_eff (t - t_i)``, and the spreads follow the
Pasquill-Gifford power laws at the puff's travel distance (floored at a small
``initial_sigma`` so the source stays non-singular).

For a steady release this superposition converges to the plume solution far
downwind — a cross-check the tests assert. The module yields the operational
metrics: the **arrival time** of a threat at a receptor, the **peak** transient
concentration, and the **integrated dose** over an exposure window. All math is
deterministic side-effect-free arithmetic over the shared #PIZ GLORIA scenario.
"""

from __future__ import annotations

import math

from on_her_majestys_secret_service.dispersion_model import (
    PlumeScenario,
    pasquill_sigma,
)

__all__ = [
    "arrival_time",
    "integrated_exposure",
    "peak_of_series",
    "puff_concentration_series",
    "puff_field_time_series",
    "single_puff",
]


def single_puff(
    mass: float,
    dx: float,
    dy: float,
    z_r: float,
    release_height: float,
    sigma_h: float,
    sigma_z: float,
) -> float:
    """Contribution of one Gaussian puff to the concentration at a receptor.

    Args:
        mass: puff mass [kg] (``Q * dt``).
        dx: downwind offset of the receptor from the puff centreline [m].
        dy: crosswind offset from the puff centreline [m].
        z_r: receptor height above the ground [m].
        release_height: effective source height ``H`` [m].
        sigma_h: horizontal dispersion coefficient (used for both x and y) [m].
        sigma_z: vertical dispersion coefficient [m].

    Returns:
        Concentration [kg/m^3], including the ground-reflection image term.
    """
    if mass < 0:
        raise ValueError(f"mass must be >= 0, got {mass}")
    if sigma_h <= 0 or sigma_z <= 0:
        return 0.0
    denom = (2.0 * math.pi) ** 1.5 * sigma_h * sigma_h * sigma_z
    if denom == 0:
        return 0.0
    exp_x = math.exp(-(dx * dx) / (2.0 * sigma_h * sigma_h))
    exp_y = math.exp(-(dy * dy) / (2.0 * sigma_h * sigma_h))
    exp_z = math.exp(
        -((z_r - release_height) ** 2) / (2.0 * sigma_z * sigma_z)
    ) + math.exp(-((z_r + release_height) ** 2) / (2.0 * sigma_z * sigma_z))
    return float(mass / denom * exp_x * exp_y * exp_z)


def _puff_sigmas(
    travel_distance: float, stability: str, initial_sigma: float
) -> tuple[float, float]:
    """Horizontal/vertical puff spread at a travel distance, floored at the initial size."""
    sy, sz = pasquill_sigma(max(travel_distance, 0.0), stability)
    return max(float(sy), initial_sigma), max(float(sz), initial_sigma)


def puff_field_time_series(
    scenario: PlumeScenario,
    receptor_x: float,
    receptor_y: float,
    receptor_z: float,
    *,
    t_start: float = 0.0,
    t_end: float = 1500.0,
    dt: float = 10.0,
    elevation: float = 0.0,
    initial_sigma: float = 1.0,
) -> dict[str, list[float]]:
    """Concentration time series at a downwind receptor from a Gaussian puff train.

    Args:
        scenario: the release scenario (drives ``Q``, stability, height, wind).
        receptor_x: downwind receptor distance [m].
        receptor_y: crosswind receptor offset [m].
        receptor_z: receptor height above ground [m].
        t_start: release/observation start time [s].
        t_end: release/observation end time [s].
        dt: emission cadence and observation step [s].
        elevation: receptor elevation for valley-channeling.
        initial_sigma: initial puff size [m] (keeps the source non-singular).

    Returns:
        ``{"time": [...], "concentration": [...]}`` sampled every ``dt``.
    """
    if dt <= 0:
        raise ValueError(f"dt must be > 0, got {dt}")
    if t_end < t_start:
        raise ValueError("t_end must be >= t_start")
    if receptor_x < 0:
        raise ValueError(f"receptor_x must be >= 0, got {receptor_x}")
    if receptor_z < 0:
        raise ValueError(f"receptor_z must be >= 0, got {receptor_z}")

    u_eff = scenario.effective_wind_speed(elevation)
    q_dt = scenario.release_rate * dt
    stability = scenario.stability
    h = scenario.release_height

    times: list[float] = []
    concentrations: list[float] = []
    n = round((t_end - t_start) / dt)
    for k in range(n + 1):
        t_obs = t_start + k * dt
        total = 0.0
        # Sum every puff emitted up to this observation time.
        for j in range(k + 1):
            t_emit = t_start + j * dt
            travel = u_eff * (t_obs - t_emit)
            sigma_h, sigma_z = _puff_sigmas(travel, stability, initial_sigma)
            total += single_puff(
                q_dt,
                dx=receptor_x - travel,
                dy=receptor_y,
                z_r=receptor_z,
                release_height=h,
                sigma_h=sigma_h,
                sigma_z=sigma_z,
            )
        times.append(round(t_obs, 3))
        concentrations.append(round(total, 12))
    return {"time": times, "concentration": concentrations}


def puff_concentration_series(
    series: dict[str, list[float]],
) -> dict[str, float]:
    """Summary of a puff concentration time series: peak value, peak time, and
    final (steady) concentration."""
    times = series["time"]
    concs = series["concentration"]
    if not concs:
        return {"peak_concentration": 0.0, "peak_time": 0.0, "final_concentration": 0.0}
    peak = max(concs)
    peak_index = concs.index(peak)
    peak_time = times[peak_index] if times else 0.0
    return {
        "peak_concentration": float(peak),
        "peak_time": float(peak_time),
        "final_concentration": float(concs[-1]),
    }


def arrival_time(
    series: dict[str, list[float]],
    threshold: float,
    *,
    default: float | None = None,
) -> float | None:
    """Earliest observation time at which the concentration reaches ``threshold``.

    Returns ``None`` (or ``default``) if the threshold is never reached.
    """
    if threshold < 0:
        raise ValueError(f"threshold must be >= 0, got {threshold}")
    for t, c in zip(series["time"], series["concentration"], strict=True):
        if c >= threshold:
            return float(t)
    return default


def peak_of_series(series: dict[str, list[float]]) -> float:
    """Maximum concentration in a puff time series (0.0 for an empty series)."""
    if not series["concentration"]:
        return 0.0
    return float(max(series["concentration"]))


def integrated_exposure(
    series: dict[str, list[float]],
    dt: float = 10.0,
) -> float:
    """Time-integrated concentration (dose proxy) over the series [kg s / m^3].

    Left-Riemann sum ``sum(C_k * dt)`` over the sampled observations.
    """
    if dt <= 0:
        raise ValueError(f"dt must be > 0, got {dt}")
    return float(sum(series["concentration"]) * dt)

"""Bobsleigh-grade descent dynamics — kinematics of an alpine exfiltration line.

PIZ GLORIA's final leg rides a bobsleigh track: a point-mass slides under
gravity down a profile while friction and aerodynamic drag resist it. This
module integrates that one-dimensional equation of motion along an arbitrary
track profile (a Polyline of ``(easting, northing, elevation)`` waypoints):

    a(v) = g sin(theta) - mu g cos(theta) - k v^2,
    k    = 0.5 rho C_d A / m,

where ``theta`` is the signed track slope (positive downhill), ``mu`` the
kinetic friction, ``rho`` air density, and ``C_d A`` the drag area. A fixed
time-step Euler integration advances speed and distance; every result is
deterministic arithmetic over the fixed profile.

Because a bobsleigh line is defined as much by its **turns** as its straight
speed, the module also pairs the descent with curve physics:

* :func:`lateral_gaccel` — the lateral acceleration ``v^2 / (g R)`` a sled
  pulls through a curve of radius ``R`` at speed ``v`` (in g's);
* :func:`banked_curve_max_speed` — the maximum speed a *banked* curve can be
  taken at without losing grip,
  ``v_max = sqrt( g R (tan beta + mu_L) / (1 - mu_L tan beta) )``;
* :func:`curve_radii` — local radii of curvature (``1 / Menger_curvature``)
  along the track, and :func:`track_curvature_audit`, which combines the
  integrated speed profile with the local radii to flag any segment whose
  lateral g exceeds a safety ceiling.
"""

from __future__ import annotations

import math
from itertools import pairwise
from typing import Any, Final

#: Standard gravity [m/s^2].
G: Final[float] = 9.80665


def _cumulative_distances(points: list[tuple[float, float, float]]) -> list[float]:
    """Cumulative 3-D arc length at each waypoint (starting at 0)."""
    distances = [0.0]
    total = 0.0
    for a, b in pairwise(points):
        total += math.hypot(math.hypot(b[0] - a[0], b[1] - a[1]), b[2] - a[2])
        distances.append(total)
    return distances


def _menger_curvature(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    c: tuple[float, float, float],
) -> float:
    """Menger curvature [1/m] of three consecutive waypoints."""
    d_ab = math.dist(a, b)
    d_bc = math.dist(b, c)
    d_ca = math.dist(c, a)
    s = 0.5 * (d_ab + d_bc + d_ca)
    if d_ab <= 1e-12 or d_bc <= 1e-12 or d_ca <= 1e-12 or s <= 1e-12:
        return 0.0
    area = math.sqrt(max(0.0, s * (s - d_ab) * (s - d_bc) * (s - d_ca)))
    return 4.0 * area / (d_ab * d_bc * d_ca)


def curve_radii(points: list[tuple[float, float, float]]) -> list[float]:
    """Local radii of curvature [m] at interior waypoints (R = 1 / k)."""
    radii: list[float] = []
    for i in range(1, len(points) - 1):
        k = _menger_curvature(points[i - 1], points[i], points[i + 1])
        radii.append(1.0 / k if k > 1e-12 else float("inf"))
    return radii


def lateral_gaccel(speed: float, radius: float, *, g: float = G) -> float:
    """Lateral acceleration [g] of a sled at ``speed`` [m/s] on a curve of
    radius ``radius`` [m]: ``v^2 / (g R)``."""
    if speed < 0:
        raise ValueError(f"speed must be >= 0, got {speed}")
    if radius <= 0:
        raise ValueError(f"radius must be > 0, got {radius}")
    return float((speed * speed) / (g * radius))


def banked_curve_max_speed(
    radius: float,
    bank_deg: float,
    lateral_friction: float = 0.6,
    *,
    g: float = G,
) -> float:
    """Maximum speed [m/s] through a banked curve of radius ``radius`` [m]
    banked at ``bank_deg`` degrees.

    From the banked-friction equilibrium,

        v_max = sqrt( g R (tan beta + mu) / (1 - mu tan beta) )

    with ``mu = lateral_friction``. The denominator must stay positive (the
    bank angle cannot exceed the friction-limited over-bank).
    """
    if radius <= 0:
        raise ValueError(f"radius must be > 0, got {radius}")
    if abs(bank_deg) >= 90.0:
        raise ValueError(f"bank_deg must be strictly within (-90, 90), got {bank_deg}")
    beta = math.radians(bank_deg)
    if not (0.0 <= lateral_friction <= 1.0):
        raise ValueError(f"lateral_friction must be in [0, 1], got {lateral_friction}")
    numerator = math.tan(beta) + lateral_friction
    if numerator <= 0.0:
        # A negative-facing bank can over-cancel the friction grip; reject
        # with a clear error instead of a math-domain sqrt failure.
        raise ValueError(
            f"bank angle yields non-positive grip numerator ({numerator}); "
            "cannot take a banked curve at this combination"
        )
    denom = 1.0 - lateral_friction * math.tan(beta)
    if denom <= 1e-12:
        raise ValueError(
            "bank angle exceeds the friction-limited over-bank; denominator <= 0"
        )
    v_max = math.sqrt(g * radius * numerator / denom)
    return float(v_max)


def descent_simulation(
    points: list[tuple[float, float, float]],
    *,
    mass: float = 100.0,
    friction: float = 0.03,
    drag_area: float = 0.45,
    rho: float = 1.2,
    start_speed: float = 0.0,
    dt: float = 0.05,
    max_steps: int = 400000,
) -> dict[str, Any]:
    """Integrate a point-mass bobsleigh down a track profile.

    Args:
        points: ``(easting, northing, elevation)`` waypoints, top to bottom.
        mass: sled + rider mass [kg].
        friction: kinetic friction coefficient ``mu``.
        drag_area: aerodynamic drag area ``C_d A`` [m^2].
        rho: air density [kg/m^3].
        start_speed: initial speed at the top [m/s].
        dt: fixed integration time step [s].
        max_steps: safety cap on integration steps.

    Returns:
        A mapping with ``time``/``distance``/``speed`` arrays plus the summary
        ``total_time_s``, ``total_distance_m``, ``max_speed_m_s``,
        ``final_speed_m_s``, ``waypoint_speeds`` (speed at each waypoint's
        cumulative distance) and ``completed``.
    """
    if len(points) < 2:
        raise ValueError("descent requires at least two waypoints")
    if mass <= 0:
        raise ValueError(f"mass must be > 0, got {mass}")
    if dt <= 0:
        raise ValueError(f"dt must be > 0, got {dt}")
    if max_steps <= 0:
        raise ValueError(f"max_steps must be > 0, got {max_steps}")

    k = 0.5 * rho * drag_area / mass
    distances = _cumulative_distances(points)

    # Per-segment geometry: length, sin(theta)=drop/len, cos(theta)=run/len.
    segments: list[tuple[float, float, float]] = []
    for p, q in pairwise(points):
        run = math.hypot(q[0] - p[0], q[1] - p[1])
        segment_length = math.hypot(run, q[2] - p[2])
        sin_theta = max((p[2] - q[2]) / segment_length, 0.0)  # downhill positive
        cos_theta = run / segment_length if segment_length > 0 else 1.0
        segments.append((segment_length, sin_theta, cos_theta))

    speed = max(float(start_speed), 0.0)
    s_pos = 0.0
    t = 0.0
    times: list[float] = [0.0]
    dists: list[float] = [0.0]
    speeds: list[float] = [speed]
    waypoint_speeds: list[float] = [speed]
    waypoint_index = 1  # next waypoint whose distance we need to capture
    steps = 0

    for segment_length, sin_theta, cos_theta in segments:
        remaining = segment_length
        while remaining > 1e-9 and steps < max_steps:
            a = G * sin_theta - friction * G * cos_theta - k * speed * speed
            new_speed = speed + a * dt
            new_speed = max(new_speed, 0.0)
            # Advance the accumulated position and the segment remainder with
            # the SAME step speed (the speed at the start of the step).
            # Advancing them with different speeds let the reported distance
            # drift from the true track length (~7 % overshoot on the
            # canonical track).
            s_pos += speed * dt
            remaining -= speed * dt
            t += dt
            speed = new_speed
            steps += 1
            times.append(round(t, 6))
            dists.append(round(s_pos, 4))
            speeds.append(round(speed, 6))
            # Capture speed whenever we pass a waypoint.
            while (
                waypoint_index < len(distances)
                and s_pos >= distances[waypoint_index] - 1e-9
            ):
                waypoint_speeds.append(speed)
                waypoint_index += 1
        if steps >= max_steps:
            break

    # Ensure every waypoint got a speed (final waypoints may be reached exactly).
    while waypoint_index < len(distances):
        waypoint_speeds.append(speed)
        waypoint_index += 1

    max_speed = max(speeds)
    return {
        "time": times,
        "distance": dists,
        "speed": speeds,
        "total_time_s": round(t, 3),
        "total_distance_m": round(float(distances[-1]), 3),
        "max_speed_m_s": round(float(max_speed), 3),
        "final_speed_m_s": round(float(speed), 3),
        "waypoint_speeds": waypoint_speeds,
        "completed": steps < max_steps,
    }


def track_curvature_audit(
    points: list[tuple[float, float, float]],
    *,
    max_g: float = 4.0,
    **descent_kwargs: Any,
) -> dict[str, Any]:
    """Combine descent speeds with local curvature to audit a track's g-load.

    Runs :func:`descent_simulation` and, at every interior waypoint, computes
    the lateral g pulled from the local radius of curvature and the speed the
    sled carries through that station.

    Returns the per-station laterals, the maximum lateral g, the number of
    stations exceeding ``max_g``, and a ``safe`` verdict.
    """
    if len(points) < 3:
        raise ValueError("curvature audit requires at least three waypoints")
    sim = descent_simulation(points, **descent_kwargs)
    radii = curve_radii(points)
    waypoint_speeds = sim["waypoint_speeds"]
    laterals = [
        lateral_gaccel(waypoint_speeds[i], radii[i - 1])
        for i in range(1, len(points) - 1)
    ]
    return {
        "lateral_g": laterals,
        "max_lateral_g": round(max(laterals), 4) if laterals else 0.0,
        "over_g": sum(1 for v in laterals if v > max_g),
        "safe": all(v <= max_g for v in laterals),
        "descent": {
            k: sim[k]
            for k in ("total_time_s", "max_speed_m_s", "final_speed_m_s", "completed")
        },
    }


def canonical_bobsleigh_track() -> list[tuple[float, float, float]]:
    """A deterministic bobsleigh-grade track: fast straight + banked hairpin.

    Returns ``(easting, northing, elevation)`` waypoints describing a long
    descent into a tight hairpin — the canonical asset used for the mission's
    curve physics (max safe banked speed and g-load). Exact and reproducible.
    """
    points: list[tuple[float, float, float]] = []
    # Long straight descent, elevation 1900 -> 1700 over 500 m plan.
    for i in range(51):
        points.append((i * 10.0, 0.0, 1900.0 - 200.0 * (i / 50.0)))
    # Feed into a hairpin: semicircle radius 30 m, centre (530, 30).
    cx, cy, r, z = 530.0, 30.0, 30.0, 1700.0
    for angle_deg in range(180, -1, -10):
        rad = math.radians(angle_deg)
        points.append((cx + r * math.cos(rad), cy + r * math.sin(rad), z))
    # Short exit straight.
    for i in range(1, 21):
        points.append((560.0 + i * 10.0, 0.0, 1700.0 - 10.0 * i))
    return points


def descent_over_waypoints(
    waypoints: list[list[float]],
    **kwargs: Any,
) -> dict[str, Any]:
    """Thin helper: run :func:`descent_simulation` over ``[easting, northing,
    elevation]`` waypoints (the planner's output shape)."""
    return descent_simulation(
        [(float(w[0]), float(w[1]), float(w[2])) for w in waypoints],
        **kwargs,
    )

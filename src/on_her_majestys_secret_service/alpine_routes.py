"""Alpine route planning — bobsleigh-grade track geometry and slope safety.

PIZ GLORIA's extraction and exfiltration legs cross alpine terrain, so the
mission requires a deterministic route planner that treats every segment like a
bobsleigh line: bounded track geometry (grade and curvature) with slope-safety
gates. This module provides:

* **Geometry primitives** — :func:`slope_angle`, :func:`track_curvature` and
  :func:`straight_line_length` on a polyline of ``(easting, northing,
  elevation)`` waypoints.
* **Safety classification** — :func:`classify_segment` maps a segment's grade
  and curvature against declared thresholds into a safety verdict, and
  :func:`route_safety_report` rolls a full polyline up into a per-segment and
  overall risk assessment.
* **Bobsleigh-grade planning** — :func:`plan_safe_route` runs Dijkstra over an
  elevation grid, rejecting any step whose grade exceeds ``max_slope`` and
  costing the rest by distance plus a grade/curvature penalty, so the
  resulting line is the shortest safe track under the planner's metric.

The planner is fully deterministic: the elevation surface is a fixed analytic
field (a doubly-sinusoidal alpine test range), every neighbor transition is
fixed arithmetic, and no random draws enter the graph search.
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from typing import Any, Final, cast

__all__ = [
    "GRADE_MARGINAL",
    "GRADE_SAFE",
    "GRADE_UNSAFE",
    "RoutePoint",
    "SafetyVerdict",
    "alpine_elevation",
    "classify_segment",
    "plan_safe_route",
    "route_safety_report",
    "slope_angle",
    "straight_line_length",
    "track_curvature",
]

#: Grade (absolute slope angle, degrees) verdict thresholds. A grade strictly
#: below ``GRADE_SAFE`` is safe; between the two is marginal; at or above
#: ``GRADE_UNSAFE`` is unsafe.
GRADE_SAFE: Final[float] = 30.0
GRADE_MARGINAL: Final[float] = 35.0
GRADE_UNSAFE: Final[float] = 45.0

# Sliding scale: a segment steeper than this cannot be climbed at all.
_ABS_SLOPE_MAX: Final[float] = 50.0


@dataclass(frozen=True)
class RoutePoint:
    """A route waypoint in projected alpine coordinates.

    Attributes:
        easting: East coordinate [m] on the planning grid.
        northing: North coordinate [m] on the planning grid.
        elevation: Height above datum [m].
    """

    easting: float
    northing: float
    elevation: float

    def distance_to(self, other: RoutePoint) -> float:
        """Euclidean 3-D distance to another waypoint."""
        return math.sqrt(
            (self.easting - other.easting) ** 2
            + (self.northing - other.northing) ** 2
            + (self.elevation - other.elevation) ** 2
        )


@dataclass(frozen=True)
class SafetyVerdict:
    """Route for one polyline segment.

    Attributes:
        grade_deg: absolute slope angle of the segment centreline [degrees].
        curvature: Menger curvature of the segment [1/m].
        grade_level: ``'safe'``, ``'marginal'``, or ``'unsafe'``.
        curvature_ok: whether curvature stays under the declared cap.
        safe: whether the segment passes every declared safety gate.
    """

    grade_deg: float
    curvature: float
    grade_level: str
    curvature_ok: bool
    safe: bool


def _dist2d(a: RoutePoint, b: RoutePoint) -> float:
    return math.hypot(a.easting - b.easting, a.northing - b.northing)


def straight_line_length(points: list[RoutePoint]) -> float:
    """Sum of 3-D straight-line chord lengths between consecutive waypoints."""
    if len(points) < 2:
        return 0.0
    return sum(a.distance_to(b) for a, b in zip(points, points[1:]))


def slope_angle(a: RoutePoint, b: RoutePoint) -> float:
    """Absolute slope angle in degrees of the chord from ``a`` to ``b``."""
    run = _dist2d(a, b)
    rise = abs(b.elevation - a.elevation)
    if run <= 1e-12:
        return 90.0
    return math.degrees(math.atan2(rise, run))


def track_curvature(a: RoutePoint, b: RoutePoint, c: RoutePoint) -> float:
    """Menger curvature [1/m] of three consecutive waypoints.

    For a plane curve the Menger curvature is ``4 * area / (|ab| |bc| |ca|)``;
    this is the standard discrete proxy for a bobsleigh line's turn sharpness.
    A degenerate (collinear / coincident) triple yields curvature 0.
    """
    ab = a.distance_to(b)
    bc = b.distance_to(c)
    ca = c.distance_to(a)
    # Heron's area.
    s = 0.5 * (ab + bc + ca)
    if ab <= 1e-12 or bc <= 1e-12 or ca <= 1e-12 or s <= 1e-12:
        return 0.0
    area = math.sqrt(max(0.0, s * (s - ab) * (s - bc) * (s - ca)))
    return 4.0 * area / (ab * bc * ca)


def classify_segment(
    a: RoutePoint,
    b: RoutePoint,
    *,
    curvature: RoutePoint | None = None,
    context: RoutePoint | None = None,
    max_curvature: float = 0.25,
) -> SafetyVerdict:
    """Classify the segment ``a -> b`` against grade and curvature gates.

    Args:
        a: start waypoint.
        b: end waypoint.
        curvature: optional third waypoint used to compute the curvature (as
            ``b`` in a ``(a, curvature, b)`` triple would be ``(prev, b, next)``;
            pass the *next* waypoint ``c`` to measure the turn at ``b``).
        context: optional second neighbour for the curvature triple; ignored
            unless ``curvature`` is also given.
        max_curvature: curvature cap [1/m]; exceeding it fails the safety gate.

    Returns:
        A :class:`SafetyVerdict` for the segment.
    """
    grade = slope_angle(a, b)
    curv = 0.0
    if curvature is not None:
        curve_a = context if context is not None else a
        curv = track_curvature(curve_a, b, curvature)
    if grade >= GRADE_UNSAFE:
        grade_level = "unsafe"
    elif grade >= GRADE_SAFE:
        grade_level = "marginal"
    else:
        grade_level = "safe"
    curvature_ok = curv <= max_curvature or curv <= 1e-12
    # A segment passes the safety gate when its grade stays below the marginal
    # threshold AND its curvature is within cap.
    safe = grade < GRADE_MARGINAL and curvature_ok
    return SafetyVerdict(
        grade_deg=round(grade, 4),
        curvature=round(curv, 6),
        grade_level=grade_level,
        curvature_ok=curvature_ok,
        safe=safe,
    )


def route_safety_report(
    points: list[RoutePoint],
    *,
    max_curvature: float = 0.25,
) -> dict[str, object]:
    """Return a per-segment and aggregate safety assessment for a polyline.

    Returns a deterministic mapping with ``segments`` (a list of per-segment
    safety dictionaries), ``total_length``, ``mean_grade_deg``,
    ``max_grade_deg``, ``max_curvature``, ``unsafe_segments`` and ``safe`` (all
    segments safe).
    """
    if len(points) < 2:
        return {
            "segments": [],
            "total_length": 0.0,
            "mean_grade_deg": 0.0,
            "max_grade_deg": 0.0,
            "max_curvature": 0.0,
            "unsafe_segments": 0,
            "safe": True,
        }
    segments: list[dict[str, object]] = []
    max_grade = 0.0
    max_curv = 0.0
    unsafe = 0
    for i in range(len(points) - 1):
        a, b = points[i], points[i + 1]
        next_p = points[i + 2] if i + 2 < len(points) else None
        prev = points[i - 1] if i > 0 else None
        verdict = classify_segment(
            a, b, curvature=next_p, context=prev, max_curvature=max_curvature
        )
        max_grade = max(max_grade, verdict.grade_deg)
        max_curv = max(max_curv, verdict.curvature)
        if not verdict.safe:
            unsafe += 1
        segments.append(
            {
                "from": i,
                "to": i + 1,
                "grade_deg": verdict.grade_deg,
                "curvature": verdict.curvature,
                "grade_level": verdict.grade_level,
                "safe": verdict.safe,
            }
        )
    grades = [float(cast("Any", s["grade_deg"])) for s in segments]
    return {
        "segments": segments,
        "total_length": round(straight_line_length(points), 3),
        "mean_grade_deg": round(sum(grades) / len(grades), 4),
        "max_grade_deg": round(max_grade, 4),
        "max_curvature": round(max_curv, 6),
        "unsafe_segments": unsafe,
        "safe": unsafe == 0,
    }


def alpine_elevation(easting: float, northing: float) -> float:
    """Analytic, deterministic alpine test surface [m].

    A doubly-sinusoidal range with a valley run along the north axis — a
    standing-in for real terrain data that is exact, reproducible, and safe to
    navigate in tests. The gradient magnitude stays well below an impassable
    cliff so the planner always has a feasible route.
    """
    return (
        1500.0 + 220.0 * math.sin(northing / 180.0) + 120.0 * math.sin(easting / 240.0)
    )


def plan_safe_route(
    *,
    start: tuple[int, int],
    goal: tuple[int, int],
    max_slope: float = GRADE_MARGINAL - 5.0,
    grid: int = 40,
    elevation_func=None,
) -> dict[str, object]:
    """Plan the lowest-cost *safe* route on a square elevation grid.

    Runs Dijkstra with 8-connectivity. A step whose chord grade exceeds
    ``max_slope`` is rejected (infeasible). Cost of an allowed step is the 3-D
    distance plus a grade penalty, so the planner prefers flatter, shorter
    tracks — a bobsleigh-grade routing objective.

    Args:
        start: ``(row, col)`` grid coordinates of the start.
        goal: ``(row, col)`` grid coordinates of the goal.
        max_slope: maximum acceptable step grade in degrees (safety gate).
        grid: number of cells along one axis.
        elevation_func: callable ``(easting, northing) -> elevation``; defaults
            to :func:`alpine_elevation`.

    Returns:
        A deterministic mapping with ``found``, ``path`` (list of
        ``(row, col)``), ``waypoints`` (list of ``[easting, northing,
        elevation]``), ``distance``, ``mean_grade_deg``, and ``safe``.
    """
    if grid < 3:
        raise ValueError(f"grid must be >= 3, got {grid}")
    for (r, c), label in ((start, "start"), (goal, "goal")):
        if not (0 <= r < grid and 0 <= c < grid):
            raise ValueError(f"{label} ({r}, {c}) outside {grid}x{grid} grid")
    elev = elevation_func if elevation_func is not None else alpine_elevation
    cell = 100.0  # metres per grid cell (a 10 km x 10 km range)

    def point(r: int, c: int) -> RoutePoint:
        return RoutePoint(
            easting=c * cell, northing=r * cell, elevation=elev(c * cell, r * cell)
        )

    # (cost, row, col, came_from)
    best: dict[tuple[int, int], float] = {start: 0.0}
    prev: dict[tuple[int, int], tuple[int, int]] = {}
    frontier: list[tuple[float, int, int]] = [(0.0, start[0], start[1])]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    while frontier:
        cost, r, c = heapq.heappop(frontier)
        key = (r, c)
        if cost > best.get(key, float("inf")):
            continue
        if key == goal:
            break
        cur_p = point(r, c)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < grid and 0 <= nc < grid):
                continue
            nxt = point(nr, nc)
            grade = slope_angle(cur_p, nxt)
            if grade > max_slope:
                continue
            dist = cur_p.distance_to(nxt)
            step_cost = dist * (1.0 + max(0.0, grade) / 90.0)
            new_cost = cost + step_cost
            nkey = (nr, nc)
            if new_cost < best.get(nkey, float("inf")):
                best[nkey] = new_cost
                prev[nkey] = (r, c)
                heapq.heappush(frontier, (new_cost, nr, nc))
    else:
        return {
            "found": False,
            "path": [],
            "waypoints": [],
            "distance": 0.0,
            "mean_grade_deg": 0.0,
            "safe": False,
        }

    # Reconstruct path.
    cells: list[tuple[int, int]] = []
    cur = goal
    while cur != start:
        cells.append(cur)
        cur = prev[cur]
    cells.append(start)
    cells.reverse()

    waypoints = [
        [p.easting, p.northing, p.elevation] for p in (point(r, c) for r, c in cells)
    ]
    safety = cast(
        "dict[str, Any]", route_safety_report([point(r, c) for r, c in cells])
    )
    return {
        "found": True,
        "path": cells,
        "waypoints": waypoints,
        "distance": round(float(safety["total_length"]), 3),
        "mean_grade_deg": float(safety["mean_grade_deg"]),
        "safe": bool(safety["safe"]),
    }

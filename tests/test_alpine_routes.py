"""Real-data tests for the alpine route planner and slope-safety model."""

from __future__ import annotations

import math

import pytest

from on_her_majestys_secret_service.alpine_routes import (
    RoutePoint,
    SafetyVerdict,
    alpine_elevation,
    classify_segment,
    plan_safe_route,
    route_safety_report,
    slope_angle,
    straight_line_length,
    track_curvature,
)


def _p(east: float, north: float, elev: float) -> RoutePoint:
    return RoutePoint(easting=east, northing=north, elevation=elev)


# --------------------------------------------------------------------------- #
# Geometry primitives
# --------------------------------------------------------------------------- #
class TestGeometry:
    def test_distance_to(self) -> None:
        a = _p(0.0, 0.0, 0.0)
        b = _p(3.0, 4.0, 12.0)  # 3-4-12-13 Pythagorean triple in 3-D
        assert a.distance_to(b) == pytest.approx(13.0)

    def test_straight_line_length_empty_and_single(self) -> None:
        assert straight_line_length([]) == 0.0
        assert straight_line_length([_p(0, 0, 0)]) == 0.0

    def test_straight_line_length_sums(self) -> None:
        points = [_p(0, 0, 0), _p(3, 0, 0), _p(3, 4, 0)]
        assert straight_line_length(points) == pytest.approx(7.0)

    def test_slope_angle_flat(self) -> None:
        assert slope_angle(_p(0, 0, 10), _p(100, 0, 10)) == pytest.approx(0.0)

    def test_slope_angle_vertical_chord(self) -> None:
        # Identical plan-position -> treated as a 90 deg face.
        assert slope_angle(_p(0, 0, 0), _p(0, 0, 50)) == pytest.approx(90.0)

    def test_slope_angle_45(self) -> None:
        assert slope_angle(_p(0, 0, 0), _p(100, 0, 100)) == pytest.approx(45.0)

    def test_curvature_straight_line_is_zero(self) -> None:
        assert track_curvature(_p(0, 0, 0), _p(1, 0, 0), _p(2, 0, 0)) == pytest.approx(0.0)

    def test_curvature_degenerate_triple_is_zero(self) -> None:
        assert track_curvature(_p(0, 0, 0), _p(0, 0, 0), _p(1, 0, 0)) == 0.0

    def test_curvature_half_turn_positive(self) -> None:
        # Three points making a right angle -> positive curvature.
        k = track_curvature(_p(0, 0, 0), _p(1, 0, 0), _p(1, 1, 0))
        assert k > 0.0


# --------------------------------------------------------------------------- #
# Segment classification
# --------------------------------------------------------------------------- #
class TestClassifySegment:
    def test_safe_flat_segment(self) -> None:
        verdict = classify_segment(_p(0, 0, 100), _p(100, 0, 110))
        assert verdict.grade_level == "safe"
        assert verdict.safe is True

    def test_marginal_segment(self) -> None:
        # ~40 deg grade -> marginal tier (>= 30, < 45) and FAILS the 35-deg gate.
        verdict = classify_segment(_p(0, 0, 0), _p(100, 0, 84.0))
        assert verdict.grade_level == "marginal"
        assert verdict.safe is False

    def test_marginal_tier_still_passes_at_under_35(self) -> None:
        # ~31.5 deg grade -> marginal tier but below the 35-deg safety gate.
        verdict = classify_segment(_p(0, 0, 0), _p(100, 0, 61.2))
        assert verdict.grade_level == "marginal"
        assert verdict.safe is True

    def test_unsafe_segment(self) -> None:
        # ~54 deg -> unsafe (>= 45).
        verdict = classify_segment(_p(0, 0, 0), _p(100, 0, 140.0))
        assert verdict.grade_level == "unsafe"

    def test_curvature_gate_fails_safe_grade(self) -> None:
        # Flat grade but a hairpin turn above the curvature cap.
        a, b, c = _p(0, 0, 10), _p(1, 0, 10), _p(1, 0.01, 10)
        verdict = classify_segment(a, b, curvature=c, max_curvature=0.05)
        assert verdict.curvature_ok is False
        assert verdict.safe is False

    def test_returns_typed_verdict(self) -> None:
        verdict = classify_segment(_p(0, 0, 0), _p(100, 0, 0))
        assert isinstance(verdict, SafetyVerdict)


class TestRouteSafetyReport:
    def test_short_route_defaults(self) -> None:
        report = route_safety_report([_p(0, 0, 0)])
        assert report["safe"] is True
        assert report["segments"] == []

    def test_full_report_on_safe_route(self) -> None:
        points = [_p(0, 0, 0), _p(100, 0, 5), _p(200, 0, 10)]
        report = route_safety_report(points)
        assert report["segments"]
        assert report["unsafe_segments"] == 0
        assert report["safe"] is True
        assert report["total_length"] > 0.0

    def test_counts_unsafe_segments(self) -> None:
        points = [_p(0, 0, 0), _p(100, 0, 200), _p(200, 0, 10)]  # first seg unsafe, second near-0? no
        report = route_safety_report(points)
        # Segment 0 rises 200 m over ~100 m chord -> unsafe; segment 1 descends.
        assert report["unsafe_segments"] >= 1
        assert report["safe"] is False


# --------------------------------------------------------------------------- #
# Planner
# --------------------------------------------------------------------------- #
class TestPlanSafeRoute:
    def test_finds_safe_route_across_range(self) -> None:
        route = plan_safe_route(start=(5, 5), goal=(34, 35), max_slope=30.0, grid=40)
        assert route["found"] is True
        assert route["safe"] is True
        assert len(route["path"]) >= 2
        assert route["distance"] > 0.0
        # Path endpoints respected.
        assert route["path"][0] == (5, 5)
        assert route["path"][-1] == (34, 35)

    def test_route_is_slopegated(self) -> None:
        route = plan_safe_route(start=(0, 0), goal=(39, 39), max_slope=30.0, grid=40)
        waypoints = route["waypoints"]
        assert waypoints
        mean_grade = float(route["mean_grade_deg"])
        assert 0.0 <= mean_grade <= 30.0

    def test_infallible_path_on_flat_terrain_is_straight(self) -> None:
        def flat(_e: float, _n: float) -> float:
            return 100.0

        route = plan_safe_route(start=(0, 0), goal=(3, 3), max_slope=45.0, grid=10, elevation_func=flat)
        assert route["found"] is True
        # Manhattan-style shortest 8-connected path has 3 moves.
        assert len(route["path"]) == 4

    def test_impassable_barrier_returns_not_found(self) -> None:
        def wall(easting: float, _northing: float) -> float:
            return 5000.0 if easting >= 20.0 * 100.0 else 0.0

        route = plan_safe_route(
            start=(5, 5),
            goal=(30, 35),
            max_slope=30.0,
            grid=40,
            elevation_func=wall,
        )
        assert route["found"] is False
        assert route["safe"] is False

    def test_invalid_grid(self) -> None:
        with pytest.raises(ValueError):
            plan_safe_route(start=(0, 0), goal=(1, 1), grid=2)

    def test_out_of_bounds_start(self) -> None:
        with pytest.raises(ValueError):
            plan_safe_route(start=(-1, 0), goal=(1, 1), grid=10)

    def test_out_of_bounds_goal(self) -> None:
        with pytest.raises(ValueError):
            plan_safe_route(start=(0, 0), goal=(10, 10), grid=10)


class TestAlpineElevation:
    def test_analytic_surface_stays_in_amplitude_band(self) -> None:
        # Base 1500 m with sinusoidal amplitude 220 (northing) + 120 (easting).
        assert math.isfinite(alpine_elevation(0.0, 0.0))
        for east in (0.0, 1000.0, 5000.0):
            for north in (0.0, 2000.0, 4000.0):
                value = alpine_elevation(east, north)
                assert 1160.0 <= value <= 1840.0, (east, north, value)

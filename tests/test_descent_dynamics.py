"""Real-data tests for the bobsleigh descent dynamics and banked-curve physics."""

from __future__ import annotations

import math

import pytest

from on_her_majestys_secret_service.descent_dynamics import (
    banked_curve_max_speed,
    canonical_bobsleigh_track,
    curve_radii,
    descent_over_waypoints,
    descent_simulation,
    lateral_gaccel,
    track_curvature_audit,
)


def _flat_track() -> list[tuple[float, float, float]]:
    return [(i * 10.0, 0.0, 2000.0) for i in range(11)]


class TestBankedCurve:
    def test_banked_max_speed_increases_with_bank(self) -> None:
        flat = banked_curve_max_speed(30.0, 0.0)
        banked = banked_curve_max_speed(30.0, 45.0)
        assert banked > flat > 0.0

    def test_invalid_radius(self) -> None:
        with pytest.raises(ValueError):
            banked_curve_max_speed(0.0, 30.0)

    def test_invalid_friction(self) -> None:
        with pytest.raises(ValueError):
            banked_curve_max_speed(30.0, 30.0, lateral_friction=1.5)

    def test_overbank_denominator(self) -> None:
        # tan(70) * 0.6 > 1 -> denominator <= 0 -> over-bank rejection.
        with pytest.raises(ValueError):
            banked_curve_max_speed(30.0, 70.0, lateral_friction=0.6)

    def test_non_positive_grip_numerator_rejected(self) -> None:
        """Round-2 regression: a negative-facing (down-hill-tilted) bank that
        would make the grip numerator non-positive must raise a clear
        ValueError, never an obscure math-domain sqrt error."""
        with pytest.raises(ValueError):
            banked_curve_max_speed(30.0, -70.0, lateral_friction=0.6)

    def test_bank_at_or_beyond_vertical_rejected(self) -> None:
        with pytest.raises(ValueError):
            banked_curve_max_speed(30.0, 90.0)
        with pytest.raises(ValueError):
            banked_curve_max_speed(30.0, -90.0)

    def test_lateral_g(self) -> None:
        assert lateral_gaccel(0.0, 30.0) == 0.0
        assert lateral_gaccel(30.0, 30.0) == pytest.approx(900.0 / (9.80665 * 30.0))

    def test_lateral_g_errors(self) -> None:
        with pytest.raises(ValueError):
            lateral_gaccel(-1.0, 30.0)
        with pytest.raises(ValueError):
            lateral_gaccel(10.0, 0.0)


class TestCurvature:
    def test_curvature_radii_straight_is_inf(self) -> None:
        assert all(r == float("inf") for r in curve_radii(_flat_track()))

    def test_hairpin_has_finite_radius(self) -> None:
        track = canonical_bobsleigh_track()
        finite = [r for r in curve_radii(track) if r != float("inf")]
        assert finite
        assert min(finite) < 50.0  # a genuine tight hairpin

    def test_radii_length(self) -> None:
        track = canonical_bobsleigh_track()
        assert len(curve_radii(track)) == len(track) - 2


class TestDescentSimulation:
    def test_descents_the_canonical_track(self) -> None:
        track = canonical_bobsleigh_track()
        sim = descent_simulation(track)
        assert sim["completed"] is True
        assert sim["total_time_s"] > 0.0
        assert sim["max_speed_m_s"] > 0.0
        assert sim["final_speed_m_s"] > 0.0

    def test_faster_with_less_friction(self) -> None:
        track = canonical_bobsleigh_track()
        low_fric = descent_simulation(track, friction=0.01)
        high_fric = descent_simulation(track, friction=0.08)
        assert low_fric["max_speed_m_s"] > high_fric["max_speed_m_s"]

    def test_waypoint_speeds_length(self) -> None:
        track = canonical_bobsleigh_track()
        sim = descent_simulation(track)
        assert len(sim["waypoint_speeds"]) == len(track)

    def test_deterministic(self) -> None:
        track = canonical_bobsleigh_track()
        a = descent_simulation(track)
        b = descent_simulation(track)
        assert a["total_time_s"] == b["total_time_s"]

    def test_error_branches(self) -> None:
        with pytest.raises(ValueError):
            descent_simulation([(0.0, 0.0, 0.0)])
        with pytest.raises(ValueError):
            descent_simulation([(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)], mass=0.0)
        with pytest.raises(ValueError):
            descent_simulation([(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)], dt=0.0)
        with pytest.raises(ValueError):
            descent_simulation([(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)], max_steps=0)

    def test_max_steps_cap_completion_false(self) -> None:
        # A tiny step cap on a long track leaves the descent incomplete.
        sim = descent_simulation(canonical_bobsleigh_track(), dt=1.0, max_steps=2)
        assert sim["completed"] is False

    def test_descent_over_waypoints(self) -> None:
        waypoints = [[0.0, 0.0, 500.0], [100.0, 0.0, 400.0], [200.0, 0.0, 300.0]]
        sim = descent_over_waypoints(waypoints)
        assert sim["total_time_s"] > 0.0


class TestTrackAudit:
    def test_flat_track_is_safe(self) -> None:
        audit = track_curvature_audit(_flat_track())
        assert audit["safe"] is True
        assert audit["max_lateral_g"] == 0.0

    def test_hairpin_track_exceeds_max_g(self) -> None:
        audit = track_curvature_audit(canonical_bobsleigh_track(), max_g=4.0)
        assert audit["max_lateral_g"] > 4.0
        assert audit["over_g"] >= 1
        assert audit["safe"] is False

    def test_audit_error_branch(self) -> None:
        with pytest.raises(ValueError):
            track_curvature_audit([(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)])


class TestCanonicalTrack:
    def test_track_is_long_and_descending(self) -> None:
        track = canonical_bobsleigh_track()
        assert len(track) > 30
        assert track[0][2] > track[-1][2]

    def test_track_deterministic(self) -> None:
        assert canonical_bobsleigh_track() == canonical_bobsleigh_track()


class TestDescentDistance:
    def test_total_distance_matches_track_arc_length(self) -> None:
        """Round-2 regression: the reported total descent distance must be the
        track's true arc length, not the stepped-position overshoot.

        A previous bookkeeping bug advanced the accumulated position with the
        step-start speed but the segment remainder with the step-end speed,
        inflating total_distance_m by ~68 m (~7 %) on the canonical track
        (1032.6 vs 964.5 m). This test pins the metric to the geometry so the
        bug cannot return undetected.
        """
        track = canonical_bobsleigh_track()
        arc = sum(math.dist(a, b) for a, b in zip(track, track[1:]))
        sim = descent_simulation(track)
        assert sim["total_distance_m"] == pytest.approx(arc, rel=1e-6)

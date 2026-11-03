"""Real-data tests for the cover-timeline verification model."""

from __future__ import annotations

import pytest

from on_her_majestys_secret_service.identity_timeline import (
    TimelineEvent,
    canonical_timeline,
    matched_minutes,
    timeline_conflicts,
    timeline_consistency,
    total_observed_minutes,
    uncovered_windows,
)


def _ev(start: float, end: float, location: str) -> TimelineEvent:
    return TimelineEvent(start=start, end=end, location=location)


class TestTimelineEvent:
    def test_valid(self) -> None:
        assert _ev(0.0, 10.0, "london").location == "london"

    def test_negative_start(self) -> None:
        with pytest.raises(ValueError):
            TimelineEvent(-1.0, 10.0, "london")

    def test_end_before_start(self) -> None:
        with pytest.raises(ValueError):
            _ev(10.0, 5.0, "london")

    def test_empty_location(self) -> None:
        with pytest.raises(ValueError):
            _ev(0.0, 10.0, "  ")


class TestTimeline:
    def test_total_observed_minutes(self) -> None:
        _claims, obs = canonical_timeline()
        assert total_observed_minutes(obs) == pytest.approx(360.0)
        assert total_observed_minutes([]) == 0.0

    def test_matched_minutes_canonical(self) -> None:
        claims, obs = canonical_timeline()
        assert matched_minutes(claims, obs) == pytest.approx(280.0)

    def test_matched_minutes_no_claims(self) -> None:
        _claims, obs = canonical_timeline()
        assert matched_minutes((), obs) == 0.0

    def test_overlapping_same_location_claims_are_not_double_counted(self) -> None:
        """Round-2 regression: two overlapping same-location claims covering an
        observation must count the union (80 min), not their sum capped at the
        observation (100 min). A previous version double-counted and could
        falsely hold a cover whose true union coverage was below the gate."""
        claims = (_ev(0, 80, "gstaad"), _ev(20, 40, "gstaad"))
        obs = (_ev(0, 100, "gstaad"),)
        assert matched_minutes(claims, obs) == pytest.approx(80.0)
        c = timeline_consistency(claims, obs)
        assert c["matched_min"] == pytest.approx(80.0)
        assert c["coverage"] == pytest.approx(0.8)
        assert c["held"] is True  # 0.8 is exactly the coverage gate

    def test_conflicts_canonical(self) -> None:
        claims, obs = canonical_timeline()
        conflicts = timeline_conflicts(claims, obs)
        assert len(conflicts) == 1
        assert conflicts[0]["observed_location"] == "london"
        assert conflicts[0]["claimed_location"] == "piz_gloria"

    def test_no_conflict_when_locations_agree(self) -> None:
        claims = (_ev(0, 100, "gstaad"),)
        obs = (_ev(50, 60, "gstaad"),)
        assert timeline_conflicts(claims, obs) == []

    def test_no_conflict_without_overlap(self) -> None:
        claims = (_ev(0, 50, "gstaad"),)
        obs = (_ev(100, 150, "london"),)
        assert timeline_conflicts(claims, obs) == []

    def test_consistency_canonical_medium(self) -> None:
        claims, obs = canonical_timeline()
        result = timeline_consistency(claims, obs)
        assert result["coverage"] == pytest.approx(0.7778, abs=1e-3)
        assert result["conflicts"] == 1
        assert result["verdict"] == "medium"
        assert result["held"] is False

    def test_consistency_held_high(self) -> None:
        claims = (_ev(0, 240, "gstaad"),)
        obs = (_ev(0, 120, "gstaad"), _ev(120, 240, "gstaad"))
        result = timeline_consistency(claims, obs)
        assert result["held"] is True
        assert result["verdict"] == "high"
        assert result["conflicts"] == 0

    def test_consistency_empty_observations(self) -> None:
        result = timeline_consistency((_ev(0, 10, "x"),), ())
        assert result["coverage"] == 0.0
        assert result["verdict"] == "low"
        assert result["held"] is False

    def test_consistency_low_when_uncovered(self) -> None:
        claims = (_ev(0, 10, "gstaad"),)
        obs = (_ev(100, 200, "london"),)
        result = timeline_consistency(claims, obs)
        assert result["coverage"] == 0.0
        assert result["verdict"] == "low"

    def test_uncovered_windows_canonical(self) -> None:
        claims, _ = canonical_timeline()
        gap = uncovered_windows(claims)
        assert gap == [(1080.0, 1440.0)]

    def test_uncovered_windows_none_when_covered(self) -> None:
        claims = (_ev(0, 1440, "gstaad"),)
        assert uncovered_windows(claims) == []

    def test_uncovered_windows_invalid_window(self) -> None:
        with pytest.raises(ValueError):
            uncovered_windows((_ev(0, 10, "x"),), window=(10.0, 0.0))

    def test_uncovered_windows_empty_claims(self) -> None:
        assert uncovered_windows((), window=(0.0, 100.0)) == [(0.0, 100.0)]


class TestCanonicalTimeline:
    def test_returns_claims_and_observations(self) -> None:
        claims, obs = canonical_timeline()
        assert len(claims) == 3
        assert len(obs) == 4
        assert claims[0].activity == "genealogical research"

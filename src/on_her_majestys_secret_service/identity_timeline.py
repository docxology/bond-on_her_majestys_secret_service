"""Cover-identity timeline verification — does the Bray persona's story hold?

A cover is only as strong as its **timeline**: every minute the persona claims
to be somewhere it can be struck by a contradicting observation. This module
verifies the claimed alibi timeline of the Bray cover against a set of
independently observed sightings.

The model is interval arithmetic over half-open ``[start, end)`` events. Each
:class:`TimelineEvent` names a location for a window of (mission) minutes.
An *observation* is *matched* when at least one claimed event overlaps it in
time **and** agrees on location; it *conflicts* when an overlapping claim names
a different location (a contradiction — e.g. the cover seen in London while
claiming Piz Gloria). The aggregate consistency score is the fraction of
observed time matched, and a discrete verdict maps the score to
``high``/``medium``/``low`` trust tiers.

Deterministic by construction: fixed claims, fixed observations, pure set
arithmetic. :func:`canonical_timeline` is the single source of truth used by
both the mission adapter and the tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "TimelineEvent",
    "canonical_timeline",
    "matched_minutes",
    "timeline_conflicts",
    "timeline_consistency",
    "total_observed_minutes",
    "uncovered_windows",
]

#: Half-open time window over which the mission timeline is audited [minutes].
MISSION_WINDOW: tuple[float, float] = (0.0, 1440.0)


@dataclass(frozen=True)
class TimelineEvent:
    """A claimed or observed event occupying a half-open time window.

    Attributes:
        start: start of the window (minutes into the mission, >= 0).
        end: end of the window (>= start).
        location: location key the subject was at during the window.
        activity: free-form activity label (informational).
    """

    start: float
    end: float
    location: str
    activity: str = ""

    def __post_init__(self) -> None:
        if self.start < 0:
            raise ValueError(f"event start must be >= 0, got {self.start}")
        if self.end < self.start:
            raise ValueError(f"event end must be >= start ({self.start}), got {self.end}")
        if not self.location.strip():
            raise ValueError("event location must be a non-empty string")


def _overlap(a: TimelineEvent, b: TimelineEvent) -> float:
    """Minutes of overlap between two half-open intervals (0 if none)."""
    return max(0.0, min(a.end, b.end) - max(a.start, b.start))


def total_observed_minutes(observations: tuple[TimelineEvent, ...] | list[TimelineEvent]) -> float:
    """Total audited minutes across all observations (union-free sum)."""
    return float(sum(event.end - event.start for event in observations))


def _union_length(intervals: list[tuple[float, float]]) -> float:
    """Length of the union of half-open intervals (overlaps merged)."""
    if not intervals:
        return 0.0
    intervals = sorted(intervals)
    total = 0.0
    cur_s, cur_e = intervals[0]
    for s, e in intervals[1:]:
        if s <= cur_e:
            cur_e = max(cur_e, e)
        else:
            total += cur_e - cur_s
            cur_s, cur_e = s, e
    total += cur_e - cur_s
    return total


def matched_minutes(
    claims: tuple[TimelineEvent, ...] | list[TimelineEvent],
    observations: tuple[TimelineEvent, ...] | list[TimelineEvent],
) -> float:
    """Observed minutes matched by a same-location overlapping claim.

    Per observation, the matching claims are merged into a union of covered
    intervals before summing, so two overlapping same-location claims never
    double-count the shared minutes (previously this inflated coverage and
    could falsely hold a cover whose union coverage was below the gate).
    """
    matched = 0.0
    for obs in observations:
        intervals: list[tuple[float, float]] = []
        for claim in claims:
            if claim.location == obs.location:
                start = max(obs.start, claim.start)
                end = min(obs.end, claim.end)
                if end > start:
                    intervals.append((start, end))
        matched += _union_length(intervals)
    return float(matched)


def timeline_conflicts(
    claims: tuple[TimelineEvent, ...] | list[TimelineEvent],
    observations: tuple[TimelineEvent, ...] | list[TimelineEvent],
) -> list[dict[str, Any]]:
    """Enumerate observation-vs-claim contradictions (overlap + location mismatch).

    Each returned mapping has the observation index, the conflicting claim
    index, the overlap minutes, and the two locations.
    """
    conflicts: list[dict[str, Any]] = []
    for oi, obs in enumerate(observations):
        for ci, claim in enumerate(claims):
            overlap = _overlap(obs, claim)
            if overlap > 0 and claim.location != obs.location:
                conflicts.append(
                    {
                        "observation": oi,
                        "claim": ci,
                        "overlap_min": round(overlap, 3),
                        "observed_location": obs.location,
                        "claimed_location": claim.location,
                    }
                )
    return conflicts


def timeline_consistency(
    claims: tuple[TimelineEvent, ...] | list[TimelineEvent],
    observations: tuple[TimelineEvent, ...] | list[TimelineEvent],
) -> dict[str, Any]:
    """Aggregate consistency analysis of the cover's claimed timeline.

    Returns the matched/observed minutes, the coverage score in ``[0, 1]``,
    the conflict count, a discrete verdict, and a boolean ``held`` flag
    (coverage >= 0.8 and no conflicts).
    """
    total = total_observed_minutes(observations)
    if total <= 0:
        return {
            "matched_min": 0.0,
            "observed_min": 0.0,
            "coverage": 0.0,
            "conflicts": 0,
            "score": 0.0,
            "verdict": "low",
            "held": False,
        }
    matched = matched_minutes(claims, observations)
    coverage = matched / total
    conflicts = timeline_conflicts(claims, observations)
    held = coverage >= 0.8 and not conflicts
    verdict = "high" if coverage >= 0.8 else ("medium" if coverage >= 0.6 else "low")
    return {
        "matched_min": round(matched, 3),
        "observed_min": round(total, 3),
        "coverage": round(coverage, 4),
        "conflicts": len(conflicts),
        "score": round(coverage, 4),
        "verdict": verdict,
        "held": bool(held),
    }


def uncovered_windows(
    claims: tuple[TimelineEvent, ...] | list[TimelineEvent],
    window: tuple[float, float] = MISSION_WINDOW,
) -> list[tuple[float, float]]:
    """Gaps in the claimed timeline within ``window`` — minutes with no alibi.

    Returns the maximal uncovered intervals ``(start, end)``.
    """
    w_start, w_end = window
    if w_end <= w_start:
        raise ValueError("window end must exceed window start")
    merged: list[tuple[float, float]] = []
    for event in sorted(claims, key=lambda e: (e.start, e.end)):
        start = max(event.start, w_start)
        end = min(event.end, w_end)
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    gaps: list[tuple[float, float]] = []
    cursor = w_start
    for start, end in merged:
        if start > cursor:
            gaps.append((round(cursor, 3), round(start, 3)))
        cursor = max(cursor, end)
    if cursor < w_end:
        gaps.append((round(cursor, 3), round(w_end, 3)))
    return gaps


def canonical_timeline() -> tuple[tuple[TimelineEvent, ...], tuple[TimelineEvent, ...]]:
    """The canonical Bray cover timeline: claimed story vs observed sightings.

    Single source of truth shared by the mission adapter and the tests. Three
    claimed segments (archives, alpine holiday, Piz Gloria guest) are audited
    against four observations, one of which (a London sighting) contradicts
    the Piz Gloria claim — giving a non-trivial medium verdict.
    """
    claims = (
        TimelineEvent(0, 360, "college_of_arms", "genealogical research"),
        TimelineEvent(360, 720, "gstaad", "alpine holiday"),
        TimelineEvent(720, 1080, "piz_gloria", "guest of Blofeld"),
    )
    observations = (
        TimelineEvent(0, 180, "college_of_arms", "verified at the College of Arms"),
        TimelineEvent(540, 600, "gstaad", "sighted in Gstaad"),
        TimelineEvent(760, 800, "piz_gloria", "inside Piz Gloria"),
        TimelineEvent(820, 900, "london", "SIS sighting in London"),
    )
    return claims, observations

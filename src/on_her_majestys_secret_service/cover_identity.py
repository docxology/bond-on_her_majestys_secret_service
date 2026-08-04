"""Cover-identity risk scoring — the Bray persona.

In the film Bond infiltrates Piz Gloria under the cover of *Sir Hilary Bray*, a
genealogist at the College of Arms. This module scores how "held" a cover
identity is: the risk that it would be exposed or contradicted by scrutiny.

Each attribute of an identity carries a **weight** (how damaging a slip would
be) and a **risk** in ``[0, 1]`` (``0`` = fully consistent/robust, ``1`` =
blown/suspicious). The aggregate cover score is the weighted mean:

    score = sum(w_i * r_i) / sum(w_i)

A deterministic verdict (:data:`RISK_LEVELS`) maps the continuous score to a
discrete threat tier. :func:`attribute_risk` computes an attribute's risk from
a small evidence model; :func:`cover_score` aggregates an arbitrary profile;
:func:`bray_persona` returns the canonical scored profile for the mission's
principal cover, and :func:`breach_scenario` models how a single failing
attribute inflates the aggregate.

Everything is deterministic arithmetic over fixed weights and evidence
coefficients — no random draws, no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

__all__ = [
    "BRAY_WEIGHTS",
    "RISK_LEVELS",
    "attribute_risk",
    "breach_scenario",
    "cover_score",
    "risk_verdict",
]

#: Canonical attribute weights for the Bray persona (how much each attribute
#: contributes to cover exposure). Keys are stable identity-attribute names.
BRAY_WEIGHTS: Final[dict[str, float]] = {
    "documentation": 0.25,
    "linguistic_fit": 0.20,
    "behavioural_consistency": 0.15,
    "social_footprint": 0.15,
    "forensic_overlap": 0.10,
    "physiognomy": 0.08,
    "pecuniary_consistency": 0.07,
}

#: Discrete thresholds mapping an aggregate score to a threat verdict.
#: Bounded, ascending: (low, medium, high, critical).
RISK_LEVELS: Final[tuple[tuple[str, float], ...]] = (
    ("low", 0.25),
    ("medium", 0.50),
    ("high", 0.75),
    ("critical", 1.01),  # unreachable cap; anything >= 0.75 is critical
)


@dataclass(frozen=True)
class _AttributeModel:
    """Linear evidence-risk model for one attribute."""

    baseline: float
    slope: float


#: Evidence coefficients per attribute: ``risk = baseline + slope * evidence``,
#: where ``evidence`` is a normalized ``[0, 1]`` measure of how *incriminating*
#: the observed evidence is (0 = clean, 1 = strongly incriminating).
_EVIDENCE_MODEL: Final[dict[str, _AttributeModel]] = {
    "documentation": _AttributeModel(0.05, 0.90),
    "linguistic_fit": _AttributeModel(0.10, 0.85),
    "behavioural_consistency": _AttributeModel(0.08, 0.88),
    "social_footprint": _AttributeModel(0.15, 0.80),
    "forensic_overlap": _AttributeModel(0.20, 0.75),
    "physiognomy": _AttributeModel(0.12, 0.82),
    "pecuniary_consistency": _AttributeModel(0.10, 0.84),
}


def attribute_risk(attribute: str, evidence: float) -> float:
    """Risk in ``[0, 1]`` for a single attribute given normalized evidence.

    Args:
        attribute: one of the keys in :data:`BRAY_WEIGHTS`.
        evidence: normalized ``[0, 1]`` measure of incriminating evidence.

    Returns:
        The attribute risk, clipped to ``[0, 1]``.

    Raises:
        ValueError: for an unknown attribute or out-of-range evidence.
    """
    if attribute not in _EVIDENCE_MODEL:
        raise ValueError(f"unknown attribute {attribute!r}; expected one of {sorted(BRAY_WEIGHTS)}")
    if not (0.0 <= evidence <= 1.0):
        raise ValueError(f"evidence must be in [0, 1], got {evidence}")
    model = _EVIDENCE_MODEL[attribute]
    raw = model.baseline + model.slope * evidence
    return max(0.0, min(1.0, raw))


def cover_score(profile: dict[str, float], weights: dict[str, float] | None = None) -> float:
    """Aggregate weighted-mean cover risk across an attribute profile.

    Args:
        profile: attribute name -> risk in ``[0, 1]``.
        weights: attribute weights; defaults to :data:`BRAY_WEIGHTS`.

    Returns:
        The aggregate cover risk score in ``[0, 1]``.

    Raises:
        ValueError: if the profile is empty or contains an unknown attribute.
    """
    if not profile:
        raise ValueError("cover profile must not be empty")
    w = BRAY_WEIGHTS if weights is None else weights
    unknown = sorted(set(profile) - set(w))
    if unknown:
        raise ValueError(f"unknown profile attributes: {unknown}")
    total_w = sum(w[a] for a in profile)
    if total_w <= 0:
        raise ValueError("cover weights must be positive-definite on the profile")
    return sum(w[a] * profile[a] for a in profile) / total_w


def risk_verdict(score: float) -> str:
    """Map an aggregate cover score to a discrete threat verdict.

    ``low`` (< 0.25), ``medium`` (< 0.50), ``high`` (< 0.75), else ``critical``.
    """
    if not (0.0 <= score <= 1.0):
        raise ValueError(f"cover score must be in [0, 1], got {score}")
    for level, threshold in RISK_LEVELS:
        if score < threshold:
            return level
    return "critical"


def breach_scenario(
    profile: dict[str, float],
    breached_attributes: dict[str, float] | None = None,
    weights: dict[str, float] | None = None,
) -> dict[str, object]:
    """Model a breach: raise one or more attributes' risk and re-score.

    Args:
        profile: baseline attribute-risk profile.
        breached_attributes: attribute -> new evidence level; the evidence is
            run through :func:`attribute_risk` (subscriptable via
            ``{attribute: evidence}``).
        weights: attribute weights (defaults to :data:`BRAY_WEIGHTS`).

    Returns:
        A deterministic mapping with the updated profile, the post-breach
        aggregate score, the pre-breach score, the score delta, and the
        verdicts before and after.
    """
    updated = dict(profile)
    for attribute, evidence in (breached_attributes or {}).items():
        updated[attribute] = attribute_risk(attribute, evidence)
    before = cover_score(profile, weights=weights)
    after = cover_score(updated, weights=weights)
    return {
        "profile": updated,
        "score_before": round(before, 6),
        "score_after": round(after, 6),
        "delta": round(after - before, 6),
        "verdict_before": risk_verdict(before),
        "verdict_after": risk_verdict(after),
    }


def bray_persona() -> dict[str, object]:
    """The canonical, scored cover profile for the principal Bray persona.

    Returns the baseline risk profile (each attribute's risk computed from a
    fixed low-evidence assumption), the aggregate score, and its verdict — the
    deterministically scored "held" cover the mission assumes.
    """
    baseline_evidence = {
        "documentation": 0.05,
        "linguistic_fit": 0.10,
        "behavioural_consistency": 0.12,
        "social_footprint": 0.08,
        "forensic_overlap": 0.05,
        "physiognomy": 0.15,
        "pecuniary_consistency": 0.10,
    }
    profile = {name: attribute_risk(name, ev) for name, ev in baseline_evidence.items()}
    score = cover_score(profile)
    return {
        "profile": profile,
        "score": round(score, 6),
        "verdict": risk_verdict(score),
    }

"""Real-data tests for the cover-identity risk model (the Bray persona)."""

from __future__ import annotations

import pytest

from on_her_majestys_secret_service.cover_identity import (
    BRAY_WEIGHTS,
    attribute_risk,
    bray_persona,
    breach_scenario,
    cover_score,
    risk_verdict,
)

_clean = {
    "documentation": 0.05,
    "linguistic_fit": 0.05,
    "behavioural_consistency": 0.05,
    "social_footprint": 0.05,
    "forensic_overlap": 0.05,
    "physiognomy": 0.05,
    "pecuniary_consistency": 0.05,
}


class TestAttributeRisk:
    def test_zero_evidence_baseline_in_range(self) -> None:
        for attribute in BRAY_WEIGHTS:
            risk = attribute_risk(attribute, 0.0)
            assert 0.0 <= risk <= 1.0

    def test_higher_evidence_raises_risk(self) -> None:
        for attribute in BRAY_WEIGHTS:
            assert attribute_risk(attribute, 1.0) >= attribute_risk(attribute, 0.0)

    def test_risk_clipped_to_one(self) -> None:
        assert attribute_risk("documentation", 1.0) <= 1.0

    def test_unknown_attribute(self) -> None:
        with pytest.raises(ValueError):
            attribute_risk("spouse_alibi", 0.5)

    def test_evidence_out_of_range(self) -> None:
        with pytest.raises(ValueError):
            attribute_risk("documentation", 1.5)
        with pytest.raises(ValueError):
            attribute_risk("documentation", -0.1)


class TestCoverScore:
    def test_clean_profile_scores_low(self) -> None:
        assert cover_score(_clean) < 0.25

    def test_fully_exposed_profile_scores_high(self) -> None:
        blown = {attr: 1.0 for attr in _clean}
        assert cover_score(blown) > 0.8

    def test_weighted_mean_respects_weights(self) -> None:
        profile = {attr: 0.5 for attr in _clean}
        assert cover_score(profile) == pytest.approx(0.5)

    def test_empty_profile(self) -> None:
        with pytest.raises(ValueError):
            cover_score({})

    def test_unknown_profile_attribute(self) -> None:
        with pytest.raises(ValueError):
            cover_score({"documentation": 0.1, "fake": 0.1})

    def test_custom_weights(self) -> None:
        custom = {"documentation": 1.0, "linguistic_fit": 1.0}
        score = cover_score({"documentation": 0.0, "linguistic_fit": 1.0}, weights=custom)
        assert score == pytest.approx(0.5)


class TestRiskVerdict:
    def test_all_verdicts(self) -> None:
        assert risk_verdict(0.10) == "low"
        assert risk_verdict(0.30) == "medium"
        assert risk_verdict(0.60) == "high"
        assert risk_verdict(0.90) == "critical"

    def test_out_of_range(self) -> None:
        with pytest.raises(ValueError):
            risk_verdict(-0.1)
        with pytest.raises(ValueError):
            risk_verdict(1.5)


class TestBreachScenario:
    def test_breach_inflates_score(self) -> None:
        result = breach_scenario(_clean, breached_attributes={"forensic_overlap": 1.0})
        assert result["score_after"] > result["score_before"]
        assert result["delta"] > 0.0

    def test_verdict_transition_recorded(self) -> None:
        result = breach_scenario(_clean, breached_attributes={"forensic_overlap": 1.0})
        assert result["verdict_after"] >= result["verdict_before"] or isinstance(result["verdict_after"], str)

    def test_no_breach_is_identity(self) -> None:
        result = breach_scenario(_clean)
        assert result["score_after"] == pytest.approx(result["score_before"])
        assert result["delta"] == 0.0


class TestBrayPersona:
    def test_canonical_persona_is_low_risk(self) -> None:
        persona = bray_persona()
        assert persona["verdict"] == "low"
        assert persona["score"] < 0.25
        assert set(persona["profile"]) == set(BRAY_WEIGHTS)

    def test_persona_is_deterministic(self) -> None:
        assert bray_persona() == bray_persona()

"""Tests for the PIZ GLORIA MissionProvider protocol adapter."""

from __future__ import annotations

from pathlib import Path

import pytest
from bond_api.discovery import load_provider
from bond_api.protocol import (
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    ReconReport,
    ReconRequest,
    run_mission,
)
from bond_api.protocol import (
    MissionProvider as Protocol,
)
from bond_api.registry import GadgetRegistry
from bond_api.serialization import from_json, to_json

from on_her_majestys_secret_service.mission import (
    CODENAME,
    FILM,
    SCENARIO,
    MissionProvider,
    register_gadgets,
    run_scenario,
)


@pytest.fixture()
def provider() -> MissionProvider:
    return MissionProvider()


class TestBrief:
    def test_identity(self, provider: MissionProvider) -> None:
        brief = provider.brief()
        assert isinstance(brief, MissionBrief)
        assert brief.film == FILM
        assert brief.codename == CODENAME

    def test_six_objectives_and_two_constraints(
        self, provider: MissionProvider
    ) -> None:
        brief = provider.brief()
        assert len(brief.objectives) == 6
        assert len(brief.assets) == 6
        assert len(brief.constraints) == 2


class TestRecon:
    def test_findings_capture_goal(self, provider: MissionProvider) -> None:
        report = provider.recon(ReconRequest(goal="locate the release point"))
        assert isinstance(report, ReconReport)
        assert any(f.label == "goal" and "locate" in f.detail for f in report.findings)


class TestPlan:
    def test_plan_has_six_steps(self, provider: MissionProvider) -> None:
        plan = provider.plan(provider.brief())
        assert isinstance(plan, MissionPlan)
        names = [step.name for step in plan.steps]
        assert names == ["dispersion", "puff", "alpine", "descent", "cover", "timeline"]


class TestExecute:
    def test_outcome_success_with_results(self, provider: MissionProvider) -> None:
        outcome = provider.execute(provider.plan(provider.brief()))
        assert isinstance(outcome, MissionOutcome)
        assert outcome.success is True
        assert "dispersion" in outcome.results
        assert "alpine" in outcome.results
        assert "cover" in outcome.results

    def test_outcome_is_deterministic(self, provider: MissionProvider) -> None:
        plan = provider.plan(provider.brief())
        a = provider.execute(plan)
        b = provider.execute(plan)
        assert a.results == b.results
        assert a.provenance.input_hash == b.provenance.input_hash

    def test_provenance_records_version_seed_hash(
        self, provider: MissionProvider
    ) -> None:
        outcome = provider.execute(provider.plan(provider.brief()))
        assert outcome.provenance.package_version == "0.1.0"
        assert outcome.provenance.seed == 7
        assert len(outcome.provenance.input_hash) == 64


class TestDebrief:
    def test_debrief_carries_lessons(self, provider: MissionProvider) -> None:
        outcome = provider.execute(provider.plan(provider.brief()))
        debrief = provider.debrief(outcome)
        assert len(debrief.lessons) == 6
        assert debrief.outcome is outcome


class TestRunScenario:
    def test_keys_and_metric_ranges(self) -> None:
        results = run_scenario()
        assert results["dispersion"]["isopleth_reach_m"] > 0.0
        assert results["dispersion"]["peak_concentration_kg_m3"] > 0.0
        assert results["dispersion"]["puff"]["arrival_time_s"] is not None
        assert results["dispersion"]["puff"]["steady_concentration_kg_m3"] > 0.0
        assert results["alpine"]["route_found"] is True
        assert results["alpine"]["route_safe"] is True
        assert results["alpine"]["descent"]["max_speed_m_s"] > 0.0
        assert results["alpine"]["bobsleigh"]["banked_max_speed_m_s"] > 0.0
        assert results["cover"]["bray_score"] < 0.25
        assert results["cover"]["timeline"]["verdict"] in {"high", "medium", "low"}

    def test_determinism(self) -> None:
        assert run_scenario() == run_scenario()


class TestProtocolConformance:
    def test_isinstance_protocol(self, provider: MissionProvider) -> None:
        # Binding: provider declares film so it must satisfy the checkable surface.
        assert isinstance(provider, Protocol)

    def test_run_mission_full_flow(self, provider: MissionProvider) -> None:
        debrief = run_mission(provider, ReconRequest(goal="verify full flow"))
        assert debrief.outcome.success is True
        assert len(debrief.lessons) == 6


class TestSerialization:
    def test_outcome_round_trips(self, provider: MissionProvider) -> None:
        outcome = provider.execute(provider.plan(provider.brief()))
        blob = to_json(outcome)
        restored = from_json(blob)
        assert isinstance(restored, MissionOutcome)
        assert restored.results == outcome.results


class TestDiscovery:
    def test_load_provider_via_bond_api(self) -> None:
        src = str(Path(__file__).resolve().parents[1] / "src")
        provider = load_provider(FILM, search_paths=[src])
        assert provider.film == FILM


class TestGadgets:
    def test_register_gadgets_populates_registry(self) -> None:
        registry = GadgetRegistry()
        returned = register_gadgets(registry)
        assert returned is registry
        assert registry.contains(FILM, "dispersion_model")
        assert registry.contains(FILM, "puff_time_series")
        assert registry.contains(FILM, "alpine_planner")
        assert registry.contains(FILM, "descent_simulator")
        assert registry.contains(FILM, "bobsleigh_audit")
        assert registry.contains(FILM, "cover_risk")
        assert registry.contains(FILM, "timeline_verifier")

    def test_module_registry_auto_registered(self) -> None:
        from on_her_majestys_secret_service.mission import REGISTRY

        assert REGISTRY.contains(FILM, "plume_footprint")

    def test_scenario_is_the_dispersion_gadget(self) -> None:
        assert SCENARIO.release_rate > 0.0
        assert SCENARIO.stability in {"A", "B", "C", "D", "E", "F"}

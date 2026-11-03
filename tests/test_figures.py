"""Tests for figure generation (deterministic, headless)."""

from __future__ import annotations

from pathlib import Path

import pytest

from on_her_majestys_secret_service.descent_dynamics import canonical_bobsleigh_track
from on_her_majestys_secret_service.dispersion_model import PlumeScenario
from on_her_majestys_secret_service.figures import (
    render_descent_figure,
    render_dispersion_figure,
    render_puff_figure,
    render_route_figure,
)


@pytest.fixture()
def scenario() -> PlumeScenario:
    return PlumeScenario(0.05, 4.0, 25.0, stability="D", valley=400.0)


class TestDispersionFigure:
    def test_renders_png(self, tmp_path: Path, scenario: PlumeScenario) -> None:
        path = render_dispersion_figure(scenario, tmp_path / "figures" / "plume.png")
        assert path.exists()
        assert path.stat().st_size > 1000
        assert path.suffix == ".png"

    def test_matches_expected_name(
        self, tmp_path: Path, scenario: PlumeScenario
    ) -> None:
        path = render_dispersion_figure(scenario, tmp_path / "plume.png")
        assert path.name == "plume.png"


class TestPuffFigure:
    def test_renders_png(self, tmp_path: Path, scenario: PlumeScenario) -> None:
        path = render_puff_figure(scenario, tmp_path / "puff.png")
        assert path.exists()
        assert path.stat().st_size > 1000


class TestRouteFigure:
    def test_renders_with_empty_waypoints(self, tmp_path: Path) -> None:
        path = render_route_figure({"waypoints": []}, tmp_path / "route.png")
        assert path.exists()
        assert path.stat().st_size > 500

    def test_renders_with_waypoints(self, tmp_path: Path) -> None:
        waypoints = [[0.0, 0.0, 100.0], [100.0, 0.0, 150.0], [200.0, 0.0, 140.0]]
        path = render_route_figure({"waypoints": waypoints}, tmp_path / "route.png")
        assert path.exists()
        assert path.stat().st_size > 500


class TestDescentFigure:
    def test_renders_from_real_track(self, tmp_path: Path) -> None:
        from on_her_majestys_secret_service.descent_dynamics import descent_simulation

        descent = descent_simulation(canonical_bobsleigh_track())
        path = render_descent_figure(descent, tmp_path / "descent.png")
        assert path.exists()
        assert path.stat().st_size > 1000

    def test_renders_with_empty_arrays(self, tmp_path: Path) -> None:
        path = render_descent_figure(
            {"distance": [], "speed": []}, tmp_path / "descent2.png"
        )
        assert path.exists()

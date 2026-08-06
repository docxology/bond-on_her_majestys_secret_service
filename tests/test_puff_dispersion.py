"""Real-data tests for the Lagrangian Gaussian puff dispersion model."""

from __future__ import annotations

import math

import pytest

from on_her_majestys_secret_service.dispersion_model import PlumeScenario, centerline_concentration
from on_her_majestys_secret_service.puff_dispersion import (
    arrival_time,
    integrated_exposure,
    peak_of_series,
    puff_concentration_series,
    puff_field_time_series,
    single_puff,
)


def _scenario(**kwargs) -> PlumeScenario:
    defaults = dict(release_rate=0.05, wind_speed=4.0, release_height=25.0, stability="C", valley=400.0)
    defaults.update(kwargs)
    return PlumeScenario(**defaults)


def _series() -> dict[str, list[float]]:
    return puff_field_time_series(_scenario(), 2000.0, 0.0, 1.5, t_end=1500.0, dt=10.0)


class TestSinglePuff:
    def test_peak_when_puff_centred(self) -> None:
        c_centre = single_puff(0.5, dx=0.0, dy=0.0, z_r=1.5, release_height=25.0, sigma_h=20.0, sigma_z=10.0)
        c_offset = single_puff(0.5, dx=50.0, dy=0.0, z_r=1.5, release_height=25.0, sigma_h=20.0, sigma_z=10.0)
        assert c_centre > c_offset > 0.0

    def test_symmetric_in_dx(self) -> None:
        a = single_puff(0.5, dx=30.0, dy=0.0, z_r=1.5, release_height=25.0, sigma_h=20.0, sigma_z=10.0)
        b = single_puff(0.5, dx=-30.0, dy=0.0, z_r=1.5, release_height=25.0, sigma_h=20.0, sigma_z=10.0)
        assert a == pytest.approx(b)

    def test_zero_mass_or_zero_sigma(self) -> None:
        assert single_puff(0.0, 0.0, 0.0, 1.5, 25.0, 20.0, 10.0) == 0.0
        assert single_puff(0.5, 0.0, 0.0, 1.5, 25.0, 0.0, 10.0) == 0.0

    def test_negative_mass_error(self) -> None:
        with pytest.raises(ValueError):
            single_puff(-1.0, 0.0, 0.0, 1.5, 25.0, 20.0, 10.0)


class TestPuffField:
    def test_series_shape_and_nonnegativity(self) -> None:
        series = _series()
        assert len(series["time"]) == 151
        assert len(series["concentration"]) == 151
        assert all(c >= 0.0 for c in series["concentration"])

    def test_converges_to_plume_steady_state(self) -> None:
        # For a steady release the puff superposition far downwind must match
        # the plume solution at the receptor (the model cross-check).
        series = _series()
        plume = centerline_concentration(2000.0, _scenario())
        ratio = series["concentration"][-1] / plume
        assert ratio == pytest.approx(1.0, rel=0.05)

    @pytest.mark.parametrize("downwind", [800.0, 1200.0, 2000.0, 3000.0])
    def test_puff_converges_to_plume_across_downwind_range(self, downwind: float) -> None:
        """V3: the puff train must converge to the steady plume over a range of
        downwind distances where the release has had time to reach the
        receptor (not just the single 2000 m case)."""
        series = puff_field_time_series(_scenario(), downwind, 0.0, 1.5, t_end=1500.0, dt=10.0)
        plume = centerline_concentration(downwind, _scenario())
        ratio = series["concentration"][-1] / plume
        assert ratio == pytest.approx(1.0, rel=0.1)

    def test_puff_does_not_converge_before_transit(self) -> None:
        """V3 negative control: at a receptor the puff train cannot yet have
        reached within the 1500 s observation horizon (transit time >> t_end),
        so the series must NOT match the steady plume. This proves the
        convergence cross-check discriminates instead of passing trivially."""
        far = 6000.0
        series = puff_field_time_series(_scenario(), far, 0.0, 1.5, t_end=1500.0, dt=10.0)
        plume = centerline_concentration(far, _scenario())
        ratio = series["concentration"][-1] / plume
        assert ratio < 0.5

    def test_nonnegative_dt_rejects(self) -> None:
        with pytest.raises(ValueError):
            puff_field_time_series(_scenario(), 2000.0, 0.0, 1.5, dt=0.0)

    def test_inverted_window_rejects(self) -> None:
        with pytest.raises(ValueError):
            puff_field_time_series(_scenario(), 2000.0, 0.0, 1.5, t_end=100.0, t_start=500.0)

    def test_negative_receptor_rejects(self) -> None:
        with pytest.raises(ValueError):
            puff_field_time_series(_scenario(), -5.0, 0.0, 1.5)
        with pytest.raises(ValueError):
            puff_field_time_series(_scenario(), 2000.0, 0.0, -1.0)

    def test_deterministic(self) -> None:
        assert _series()["concentration"] == _series()["concentration"]


class TestPuffSummary:
    def test_puff_concentration_series(self) -> None:
        summary = puff_concentration_series(_series())
        assert summary["peak_concentration"] > 0.0
        assert summary["peak_time"] >= 0.0
        assert summary["final_concentration"] > 0.0

    def test_empty_series_summary(self) -> None:
        assert puff_concentration_series({"time": [], "concentration": []}) == {
            "peak_concentration": 0.0,
            "peak_time": 0.0,
            "final_concentration": 0.0,
        }

    def test_arrival_time_found(self) -> None:
        arrived = arrival_time(_series(), 1e-8)
        assert arrived is not None
        assert arrived >= 0.0

    def test_arrival_time_not_reached_default(self) -> None:
        assert arrival_time(_series(), 1e3, default=999.0) == 999.0
        assert arrival_time(_series(), 1e3) is None

    def test_arrival_time_negative_threshold(self) -> None:
        with pytest.raises(ValueError):
            arrival_time(_series(), -1.0)

    def test_peak_of_series(self) -> None:
        assert peak_of_series(_series()) > 0.0
        assert peak_of_series({"time": [], "concentration": []}) == 0.0

    def test_integrated_exposure(self) -> None:
        series = _series()
        dose = integrated_exposure(series, dt=10.0)
        assert dose > 0.0
        assert math.isfinite(dose)

    def test_integrated_exposure_bad_dt(self) -> None:
        with pytest.raises(ValueError):
            integrated_exposure(_series(), dt=0.0)

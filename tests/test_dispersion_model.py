"""Real-data tests for the aerosol (bioweapon) dispersion model."""

from __future__ import annotations

import math

import pytest

from on_her_majestys_secret_service.dispersion_model import (
    PG_OPEN_COUNTRY_Y,
    PG_OPEN_COUNTRY_Z,
    PlumeScenario,
    centerline_concentration,
    downwind_axis,
    ground_level_concentration,
    inhalation_dose,
    isopleth_distance,
    pasquill_sigma,
    peak_ground_concentration,
    point_concentration,
    stability_class,
    valley_wind_factor,
)


def _scenario(**kwargs) -> PlumeScenario:
    defaults = dict(
        release_rate=0.05,
        wind_speed=4.0,
        release_height=25.0,
        stability="D",
        valley=400.0,
    )
    defaults.update(kwargs)
    return PlumeScenario(**defaults)


# --------------------------------------------------------------------------- #
# Pasquill-Gifford sigma coefficients
# --------------------------------------------------------------------------- #
class TestPasquillSigma:
    def test_known_stability_classes_match_table(self) -> None:
        for stability in PG_OPEN_COUNTRY_Y:
            ay, by = PG_OPEN_COUNTRY_Y[stability]
            cz, dz = PG_OPEN_COUNTRY_Z[stability]
            sy, sz = pasquill_sigma(100.0, stability)
            assert sy == pytest.approx(ay * 100.0**by)
            assert sz == pytest.approx(cz * 100.0**dz)

    def test_coefficients_grow_with_downwind_distance(self) -> None:
        for stability in PG_OPEN_COUNTRY_Y:
            sy_near, sz_near = pasquill_sigma(50.0, stability)
            sy_far, sz_far = pasquill_sigma(1000.0, stability)
            assert sy_far > sy_near
            assert sz_far > sz_near

    def test_vertical_dispersion_capped_for_stable_classes(self) -> None:
        # Stable F suppresses vertical mixing relative to unstable A.
        _, sz_a = pasquill_sigma(500.0, "A")
        _, sz_f = pasquill_sigma(500.0, "F")
        assert sz_f < sz_a

    def test_rejects_negative_distance(self) -> None:
        with pytest.raises(ValueError):
            pasquill_sigma(-1.0, "D")

    def test_rejects_unknown_stability(self) -> None:
        with pytest.raises(ValueError):
            pasquill_sigma(100.0, "Q")


# --------------------------------------------------------------------------- #
# PlumeScenario validation & valley channeling
# --------------------------------------------------------------------------- #
class TestPlumeScenario:
    def test_invalid_release_rate(self) -> None:
        with pytest.raises(ValueError):
            _scenario(release_rate=-1.0)

    def test_invalid_wind_speed(self) -> None:
        with pytest.raises(ValueError):
            _scenario(wind_speed=0.0)

    def test_invalid_release_height(self) -> None:
        with pytest.raises(ValueError):
            _scenario(release_height=-2.0)

    def test_invalid_stability(self) -> None:
        with pytest.raises(ValueError):
            _scenario(stability="Z")

    def test_effective_wind_without_valley(self) -> None:
        s = _scenario(valley=None)
        assert s.effective_wind_speed(0.0) == pytest.approx(4.0)

    def test_effective_wind_with_valley_channeling(self) -> None:
        s = _scenario()
        factor_floor = valley_wind_factor(0.0, 400.0)
        assert s.effective_wind_speed(0.0) == pytest.approx(4.0 * factor_floor)

    def test_effective_wind_rises_with_elevation(self) -> None:
        s = _scenario()
        assert s.effective_wind_speed(0.0) < s.effective_wind_speed(200.0) < 4.0

    def test_attributes_are_floats(self) -> None:
        s = _scenario()
        assert isinstance(s.release_rate, float)
        assert str(s.stability) == "D"


class TestValleyWindFactor:
    def test_floor_factor_at_zero(self) -> None:
        assert valley_wind_factor(0.0, 400.0) == pytest.approx(0.6)

    def test_approaches_one_at_high_elevation(self) -> None:
        assert valley_wind_factor(1e6, 400.0) == pytest.approx(1.0, abs=1e-9)
        assert valley_wind_factor(200.0, 400.0) == pytest.approx(
            1.0 - 0.4 * math.exp(-0.5)
        )

    def test_monotonic_in_elevation(self) -> None:
        f0 = valley_wind_factor(0.0, 100.0)
        f1 = valley_wind_factor(100.0, 100.0)
        f2 = valley_wind_factor(1000.0, 100.0)
        assert f0 < f1 < f2

    def test_invalid_valley_depth(self) -> None:
        with pytest.raises(ValueError):
            valley_wind_factor(10.0, 0.0)

    def test_invalid_elevation(self) -> None:
        with pytest.raises(ValueError):
            valley_wind_factor(-1.0, 100.0)

    def test_invalid_floor_factor(self) -> None:
        with pytest.raises(ValueError):
            valley_wind_factor(10.0, 100.0, floor_factor=0.0)
        with pytest.raises(ValueError):
            valley_wind_factor(10.0, 100.0, floor_factor=1.5)


# --------------------------------------------------------------------------- #
# Gaussian plume concentration
# --------------------------------------------------------------------------- #
class TestConcentration:
    def test_positive_centerline_concentration(self) -> None:
        s = _scenario()
        assert centerline_concentration(500.0, s) > 0.0

    def test_symmetric_crosswind_decay(self) -> None:
        s = _scenario()
        c_on = point_concentration(500.0, 0.0, 1.5, s)
        c_off = point_concentration(500.0, 200.0, 1.5, s)
        assert c_on > c_off > 0.0

    def test_inverse_with_wind_speed(self) -> None:
        slow = _scenario(wind_speed=2.0)
        fast = _scenario(wind_speed=8.0)
        assert centerline_concentration(1000.0, slow) > centerline_concentration(
            1000.0, fast
        )

    def test_proportional_to_release_rate(self) -> None:
        low = _scenario(release_rate=0.02)
        high = _scenario(release_rate=0.08)
        assert centerline_concentration(1000.0, high) > centerline_concentration(
            1000.0, low
        )

    def test_ground_level_wrapper(self) -> None:
        s = _scenario()
        assert ground_level_concentration(500.0, 0.0, s) > 0.0
        assert ground_level_concentration(500.0, 50.0, s, receptor_height=0.0) >= 0.0

    def test_zero_release_rate(self) -> None:
        s = _scenario(release_rate=0.0)
        assert point_concentration(500.0, 0.0, 0.0, s) == 0.0

    def test_rejects_negative_downwind(self) -> None:
        with pytest.raises(ValueError):
            point_concentration(-5.0, 0.0, 0.0, _scenario())

    def test_rejects_negative_receptor_height(self) -> None:
        with pytest.raises(ValueError):
            point_concentration(5.0, 0.0, -1.0, _scenario())

    def test_peak_is_finite_and_positive(self) -> None:
        s = _scenario()
        x, c = peak_ground_concentration(s)
        assert x > 0.0
        assert c > 0.0

    def test_peak_independent_of_run(self) -> None:
        s = _scenario()
        assert peak_ground_concentration(s) == peak_ground_concentration(s)


class TestDownwindAxis:
    def test_profile_lengths(self) -> None:
        s = _scenario()
        axis = downwind_axis(5.0, 3000.0, 30, s)
        assert len(axis["distance"]) == 31
        assert len(axis["concentration"]) == 31
        assert axis["distance"][0] == pytest.approx(5.0)
        assert axis["concentration"][5] > 0.0

    def test_invalid_steps(self) -> None:
        with pytest.raises(ValueError):
            downwind_axis(0.0, 100.0, 0, _scenario())


class TestIsopleth:
    def test_lower_threshold_reaches_farther(self) -> None:
        s = _scenario()
        assert isopleth_distance(1e-6, s, max_distance=50000.0) < isopleth_distance(
            1e-8, s, max_distance=50000.0
        )

    def test_unreachable_threshold_returns_zero(self) -> None:
        s = _scenario()
        assert isopleth_distance(1e-3, s) == 0.0  # peak is ~3.5e-6 < 1e-3

    def test_always_reached_returns_window(self) -> None:
        s = _scenario()
        assert isopleth_distance(0.0, s, max_distance=500.0) == pytest.approx(500.0)

    def test_never_reached_returns_zero_even_with_valley(self) -> None:
        s = _scenario()
        assert isopleth_distance(1.0, s) == 0.0

    def test_invalid_threshold(self) -> None:
        with pytest.raises(ValueError):
            isopleth_distance(-1.0, _scenario())

    def test_invalid_max_distance(self) -> None:
        with pytest.raises(ValueError):
            isopleth_distance(1e-7, _scenario(), max_distance=0.0)


class TestInhalationDose:
    def test_dose_scales_with_exposure(self) -> None:
        d_short = inhalation_dose(1e-6, 10.0)
        d_long = inhalation_dose(1e-6, 100.0)
        assert d_long == pytest.approx(10.0 * d_short)

    def test_zero_concentration_zero_dose(self) -> None:
        assert inhalation_dose(0.0, 100.0) == 0.0

    def test_invalid_concentration(self) -> None:
        with pytest.raises(ValueError):
            inhalation_dose(-1.0, 10.0)

    def test_invalid_exposure_time(self) -> None:
        with pytest.raises(ValueError):
            inhalation_dose(1e-6, -5.0)

    def test_invalid_breathing_rate(self) -> None:
        with pytest.raises(ValueError):
            inhalation_dose(1e-6, 10.0, breathing_rate=0.0)


# --------------------------------------------------------------------------- #
# Stability-class inference
# --------------------------------------------------------------------------- #
class TestStabilityClass:
    def test_daytime_wind_brackets(self) -> None:
        assert stability_class(1.0, daytime=True) == "A"
        assert stability_class(2.5, daytime=True) == "B"
        assert stability_class(4.0, daytime=True) == "C"
        assert stability_class(6.0, daytime=True) == "D"
        assert stability_class(20.0, daytime=True) == "D"

    def test_nighttime_wind_brackets(self) -> None:
        assert stability_class(1.0, daytime=False) == "F"
        assert stability_class(2.5, daytime=False) == "E"
        assert stability_class(4.0, daytime=False) == "D"
        assert stability_class(20.0, daytime=False) == "D"

    def test_invalid_wind(self) -> None:
        with pytest.raises(ValueError):
            stability_class(-1.0)

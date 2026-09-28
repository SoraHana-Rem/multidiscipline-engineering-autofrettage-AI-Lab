"""
Integration tests for analyze_vessel orchestrator (REQ-FUN, REQ-PRC, REQ-BND).
"""
import warnings
import pytest

from src.analysis import analyze_vessel
from src.errors import PressureVesselWarning, ValidationError

TOLERANCE = 1e-4


def test_tv1_thin_wall(tv1_thin):
    """REQ-PRC-001..004: TV-1 thin-wall integration verification."""
    res = analyze_vessel(tv1_thin["P"], tv1_thin["r_i"], tv1_thin["t"], tv1_thin["sigma_y"])
    assert res.model == tv1_thin["expected_model"]
    assert pytest.approx(res.sigma_hoop, abs=TOLERANCE) == tv1_thin["sigma_hoop"]
    assert pytest.approx(res.sigma_long, abs=TOLERANCE) == tv1_thin["sigma_long"]
    assert pytest.approx(res.sigma_radial, abs=TOLERANCE) == tv1_thin["sigma_radial"]
    assert pytest.approx(res.sigma_vm, abs=TOLERANCE) == tv1_thin["sigma_vm"]
    assert pytest.approx(res.safety_factor, abs=TOLERANCE) == tv1_thin["safety_factor"]
    assert res.yielded == tv1_thin["yielded"]

def test_tv2_thick_wall():
    """TV-2 thick-wall warning and calculation verification."""
    tv2_thick = {
        "P": 10.0,
        "r_i": 500.0,
        "t": 200.0,
        "sigma_y": 500.0,
        "sigma_hoop": 30.833333333333332,
        "sigma_long": 10.416666666666666,
        "sigma_radial": -10.0,
        "sigma_vm": 35.36270398786457,
        "safety_factor": 14.13919026586839,
        "yielded": False,
    }

    with pytest.warns(PressureVesselWarning, match="Using Lamé thick-wall model"):
        res = analyze_vessel(tv2_thick["P"], tv2_thick["r_i"], tv2_thick["t"], tv2_thick["sigma_y"])

    assert res.model == "lame_thick_wall"
    assert pytest.approx(res.sigma_hoop, abs=1e-4) == tv2_thick["sigma_hoop"]
    assert pytest.approx(res.sigma_long, abs=1e-4) == tv2_thick["sigma_long"]
    assert pytest.approx(res.sigma_radial, abs=1e-4) == tv2_thick["sigma_radial"]
    assert pytest.approx(res.sigma_vm, abs=1e-4) == tv2_thick["sigma_vm"]
    assert pytest.approx(res.safety_factor, abs=1e-4) == tv2_thick["safety_factor"]
    assert res.yielded == tv2_thick["yielded"]


def test_tv3_yielding(tv3_yield):
    """REQ-FUN-005: TV-3 yielded status verification."""
    res = analyze_vessel(tv3_yield["P"], tv3_yield["r_i"], tv3_yield["t"], tv3_yield["sigma_y"])
    assert res.yielded is True
    assert pytest.approx(res.safety_factor, abs=TOLERANCE) == tv3_yield["safety_factor"]


def test_boundary_ratio_exact_10():
    """REQ-BND-001: Ratio exactly 10 must select thin_wall without issuing warning."""
    with warnings.catch_warnings(record=True) as recorded_warnings:
        warnings.simplefilter("always")
        res = analyze_vessel(2.0, 50.0, 5.0, 500.0)  # r_i / t = 10.0
        assert res.model == "thin_wall"
        pv_warnings = [w for w in recorded_warnings if issubclass(w.category, PressureVesselWarning)]
        assert len(pv_warnings) == 0


def test_boundary_ratio_just_below_10():
    """REQ-BND-002: Ratio < 10 must route to Lamé thick wall and trigger warning."""
    with pytest.warns(PressureVesselWarning, match="Using Lamé thick-wall model"):
        res = analyze_vessel(2.0, 49.95, 5.0, 500.0)  # r_i / t = 9.99
        assert res.model == "lame_thick_wall"


def test_validation_ranges_and_unit_slips():
    """REQ-INP series & REQ-BND-003: Verify input bounds catch unit mismatch slips."""
    # Catch Pa unit slip (500e6 Pa exceeds max yield 3000 MPa)
    with pytest.raises(ValidationError, match="sigma_y"):
        analyze_vessel(2.0, 50.0, 5.0, 500e6)

    # Catch GPa unit slip (0.5 GPa below min yield 10 MPa)
    with pytest.raises(ValidationError, match="sigma_y"):
        analyze_vessel(2.0, 50.0, 5.0, 0.5)

    # Catch radius in meters (0.5 m below min radius 1.0 mm)
    with pytest.raises(ValidationError, match="r_i"):
        analyze_vessel(2.0, 0.5, 5.0, 500.0)
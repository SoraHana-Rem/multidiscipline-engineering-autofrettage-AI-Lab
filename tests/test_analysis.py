"""Integration tests for vessel analysis and boundary guardrails."""

import warnings

import pytest

from src.analysis import analyze_vessel
from src.errors import PressureVesselWarning, ValidationError

TOLERANCE = 1e-4


def test_tv1_thin_wall(tv1_thin):
    """REQ-FUN-004, REQ-PRC-001, REQ-PRC-002: Verify TV-1 results."""
    res = analyze_vessel(
        tv1_thin["P"],
        tv1_thin["r_i"],
        tv1_thin["t"],
        tv1_thin["sigma_y"],
    )

    assert res.model == tv1_thin["expected_model"]
    assert res.sigma_hoop == pytest.approx(
        tv1_thin["sigma_hoop"], abs=TOLERANCE
    )
    assert res.sigma_long == pytest.approx(
        tv1_thin["sigma_long"], abs=TOLERANCE
    )
    assert res.sigma_radial == pytest.approx(
        tv1_thin["sigma_radial"], abs=TOLERANCE
    )
    assert res.sigma_vm == pytest.approx(
        tv1_thin["sigma_vm"], abs=TOLERANCE
    )
    assert res.safety_factor == pytest.approx(
        tv1_thin["safety_factor"], abs=TOLERANCE
    )
    assert res.yielded == tv1_thin["yielded"]


def test_tv2_thick_wall():
    """REQ-FUN-002, REQ-FUN-004, REQ-PRC-001, REQ-PRC-002: Verify TV-2."""
    with pytest.warns(
        PressureVesselWarning,
        match="Using Lamé thick-wall model",
    ):
        res = analyze_vessel(
            P=10.0,
            r_i=500.0,
            t=200.0,
            sigma_y=500.0,
        )

    assert res.model == "lame_thick_wall"
    assert res.sigma_hoop == pytest.approx(
        30.833333333333332, abs=TOLERANCE
    )
    assert res.sigma_long == pytest.approx(
        10.416666666666666, abs=TOLERANCE
    )
    assert res.sigma_radial == pytest.approx(
        -10.0, abs=TOLERANCE
    )
    assert res.sigma_vm == pytest.approx(
        35.36270398786457, abs=TOLERANCE
    )
    assert res.safety_factor == pytest.approx(
        14.13919026586839, abs=TOLERANCE
    )
    assert res.yielded is False


def test_tv3_yielding(tv3_yield):
    """REQ-FUN-005, REQ-PRC-002: Verify the yielding reference case."""
    res = analyze_vessel(
        tv3_yield["P"],
        tv3_yield["r_i"],
        tv3_yield["t"],
        tv3_yield["sigma_y"],
    )

    assert res.yielded is True
    assert res.safety_factor == pytest.approx(
        tv3_yield["safety_factor"], abs=TOLERANCE
    )


def test_boundary_ratio_exact_10():
    """REQ-BND-001: Ratio 10 selects thin-wall without a vessel warning."""
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        res = analyze_vessel(2.0, 50.0, 5.0, 500.0)

    assert res.model == "thin_wall"
    assert not any(
        issubclass(item.category, PressureVesselWarning)
        for item in recorded
    )


def test_boundary_ratio_just_below_10():
    """REQ-BND-002: Ratio below 10 selects Lamé and emits a warning."""
    with pytest.warns(
        PressureVesselWarning,
        match="Using Lamé thick-wall model",
    ):
        res = analyze_vessel(2.0, 49.95, 5.0, 500.0)

    assert res.model == "lame_thick_wall"


def test_validation_ranges_and_unit_slips():
    """
    REQ-BND-003: Reject example unit slips that exceed numerical bounds.

    Inputs carry no unit metadata; slips within bounds are not detectable.
    """
    with pytest.raises(ValidationError, match="sigma_y"):
        analyze_vessel(2.0, 50.0, 5.0, 500e6)

    with pytest.raises(ValidationError, match="sigma_y"):
        analyze_vessel(2.0, 50.0, 5.0, 0.5)

    with pytest.raises(ValidationError, match="r_i"):
        analyze_vessel(2.0, 0.5, 5.0, 500.0)
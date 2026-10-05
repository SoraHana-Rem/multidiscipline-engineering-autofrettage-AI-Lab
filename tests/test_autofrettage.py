import math

import pytest

from src.errors import ValidationError
from src.physics.autofrettage import (
    calculate_autofrettage,
    calculate_autofrettage_stresses,
    calculate_plastic_radius,
)


def test_plastic_radius_valid_range():
    """REQ-AUT-001: Plastic radius matches the reference case."""
    r_p = calculate_plastic_radius(
        P_auto=250.0,
        r_i=100.0,
        r_o=200.0,
        sigma_y=500.0,
    )

    assert 100.0 < r_p < 200.0
    assert r_p == pytest.approx(108.28, abs=1e-2)


def test_plastic_radius_below_yield_raises_error():
    """REQ-AUT-002: Pressure below initial yield is rejected."""
    with pytest.raises(
        ValidationError,
        match="below initial yield pressure",
    ):
        calculate_plastic_radius(
            P_auto=50.0,
            r_i=100.0,
            r_o=200.0,
            sigma_y=500.0,
        )


def test_residual_radial_stress_free_surface_boundary_conditions():
    """REQ-AUT-003: Residual radial stress vanishes at free surfaces."""
    results = calculate_autofrettage_stresses(
        250.0, 100.0, 200.0, 500.0
    )

    assert results["sigma_r_res"][0] == pytest.approx(
        0.0, abs=1e-4
    )
    assert results["sigma_r_res"][-1] == pytest.approx(
        0.0, abs=1e-4
    )


def test_plastic_radius_exceeds_full_yield_raises_error():
    """REQ-AUT-002: Pressure above full yield is rejected."""
    with pytest.raises(
        ValidationError,
        match="exceeds or equals full yield pressure",
    ):
        calculate_plastic_radius(
            P_auto=500.0,
            r_i=100.0,
            r_o=200.0,
            sigma_y=500.0,
        )


def test_residual_hoop_stress_is_compressive_at_bore():
    """REQ-AUT-003: Reference case has bore compression and outer tension."""
    results = calculate_autofrettage_stresses(
        250.0, 100.0, 200.0, 500.0
    )

    assert results["sigma_theta_res"][0] < 0.0
    assert results["sigma_theta_res"][-1] > 0.0


@pytest.mark.parametrize("boundary", ["initial", "full"])
def test_exact_yield_boundaries_rejected(boundary):
    """REQ-AUT-002: Both pressure bounds are excluded."""
    ri, ro, sy = 50.0, 70.0, 250.0

    if boundary == "initial":
        pressure = (sy / math.sqrt(3)) * (
            1.0 - (ri / ro) ** 2
        )
    else:
        pressure = (2.0 * sy / math.sqrt(3)) * math.log(ro / ri)

    with pytest.raises(ValidationError):
        calculate_plastic_radius(pressure, ri, ro, sy)


@pytest.mark.parametrize(
    "field",
    ["P_auto", "r_i", "r_o", "sigma_y"],
)
@pytest.mark.parametrize(
    "value,error",
    [
        (True, TypeError),
        ("50", TypeError),
        (float("nan"), ValidationError),
        (float("inf"), ValidationError),
        (0, ValidationError),
        (-1, ValidationError),
    ],
)
def test_invalid_autofrettage_scalars(field, value, error):
    """REQ-AUT-001, REQ-AUT-002: Invalid scalars fail at the boundary."""
    inputs = {
        "P_auto": 80.0,
        "r_i": 50.0,
        "r_o": 70.0,
        "sigma_y": 250.0,
    }
    inputs[field] = value

    with pytest.raises(error, match=field):
        calculate_autofrettage_stresses(**inputs)


@pytest.mark.parametrize("outer", [50.0, 40.0])
def test_invalid_autofrettage_geometry(outer):
    """REQ-AUT-001: Outer radius must exceed inner radius."""
    with pytest.raises(ValidationError, match="r_o"):
        calculate_plastic_radius(
            80.0, 50.0, outer, 250.0
        )


@pytest.mark.parametrize(
    "value,error",
    [
        (True, TypeError),
        (2.5, TypeError),
        (0, ValidationError),
        (1, ValidationError),
    ],
)
def test_invalid_profile_point_count(value, error):
    """REQ-AUT-003: Profile point count must be an integer of at least two."""
    with pytest.raises(error, match="num_points"):
        calculate_autofrettage_stresses(
            80.0,
            50.0,
            70.0,
            250.0,
            num_points=value,
        )


@pytest.mark.parametrize(
    "value,error",
    [
        (True, TypeError),
        ("50", TypeError),
        (float("nan"), ValidationError),
        (float("inf"), ValidationError),
        (0, ValidationError),
        (-1, ValidationError),
    ],
)
def test_invalid_working_pressure(value, error):
    """REQ-AUT-004: Supplied working pressure must be finite and positive."""
    with pytest.raises(error, match="P_working"):
        calculate_autofrettage(
            80.0,
            50.0,
            70.0,
            250.0,
            P_working=value,
        )


def test_absent_and_valid_working_pressure():
    """REQ-AUT-004: Absent SF is explicit; valid result is preserved."""
    unloaded = calculate_autofrettage(
        80.0, 50.0, 70.0, 250.0
    )
    assert unloaded.safety_factor is None

    working = calculate_autofrettage(
        80.0,
        50.0,
        70.0,
        250.0,
        P_working=50.0,
    )
    assert working.safety_factor == pytest.approx(
        1.722235692, abs=1e-6
    )
"""
Unit tests for raw input validation rules (REQ-TYP and REQ-VAL series).
"""

import pytest

from src.validation.inputs import validate_inputs

"""
Unit tests for raw input validation rules (REQ-TYP and REQ-VAL series).
"""

"""
Unit tests for raw input validation rules (REQ-TYP and REQ-VAL series).
"""


# ---------------------------------------------------------------------------
# 1. Happy Path & Valid Type Handling
# ---------------------------------------------------------------------------


def test_validate_inputs_valid_floats():
    """Valid float values should return a tuple of floats without raising errors."""
    P, r_i, t, sigma_y = validate_inputs(2.0, 500.0, 5.0, 500.0)
    assert (P, r_i, t, sigma_y) == (2.0, 500.0, 5.0, 500.0)
    assert all(isinstance(val, float) for val in (P, r_i, t, sigma_y))


def test_validate_inputs_integer_coercion():
    """REQ-TYP-001: Integer inputs should be cleanly coerced to float."""
    P, r_i, t, sigma_y = validate_inputs(2, 500, 5, 500)
    assert (P, r_i, t, sigma_y) == (2.0, 500.0, 5.0, 500.0)


# ---------------------------------------------------------------------------
# 2. Type Rejection (REQ-TYP-002 through REQ-TYP-004)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_value", [True, False])
def test_validate_inputs_rejects_bool(bad_value):
    """REQ-TYP-002: Booleans must be rejected even though bool inherits from int."""
    with pytest.raises(TypeError, match="must be a numeric float or int: got bool"):
        validate_inputs(bad_value, 500.0, 5.0, 500.0)


@pytest.mark.parametrize("bad_type", ["5.0", None, [500.0], {"t": 5.0}, 3 + 4j])
def test_validate_inputs_rejects_invalid_types(bad_type):
    """REQ-TYP-003 & REQ-TYP-004: Strings, None, collections, and complex numbers must raise TypeError."""
    with pytest.raises(TypeError, match="must be a numeric float or int"):
        validate_inputs(2.0, bad_type, 5.0, 500.0)


# ---------------------------------------------------------------------------
# 3. Finiteness & Positivity Guardrails (REQ-VAL-001 through REQ-VAL-005)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("non_finite", [float("nan"), float("inf"), float("-inf")])
def test_validate_inputs_rejects_non_finite(non_finite):
    """REQ-VAL-001: NaN and infinity values must raise ValueError."""
    with pytest.raises(ValueError, match="must be finite"):
        validate_inputs(2.0, 500.0, non_finite, 500.0)


@pytest.mark.parametrize(
    "P, r_i, t, sigma_y, expected_match",
    [
        (-1.0, 500.0, 5.0, 500.0, "Pressure must be positive"),
        (0.0, 500.0, 5.0, 500.0, "Pressure must be positive"),
        (2.0, -10.0, 5.0, 500.0, "Inner radius must be positive"),
        (2.0, 500.0, 0.0, 500.0, "Wall thickness must be positive"),
        (2.0, 500.0, 5.0, -100.0, "Yield strength must be positive"),
    ],
)
def test_validate_inputs_rejects_non_positive(P, r_i, t, sigma_y, expected_match):
    """REQ-VAL-002..REQ-VAL-005: Zero or negative values must raise ValueError with clear messages."""
    with pytest.raises(ValueError, match=expected_match):
        validate_inputs(P, r_i, t, sigma_y)


# ---------------------------------------------------------------------------
# 4. Out of Range Guardrails & Message Ordering (REQ-VAL-006 & REQ-ERR-003)
# ---------------------------------------------------------------------------


def test_validate_inputs_out_of_range():
    """REQ-VAL-006: Exceeding maximum parameter range limits must raise ValueError."""
    with pytest.raises(ValueError, match="Pressure out of range"):
        validate_inputs(150.0, 500.0, 5.0, 500.0)  # P exceeds 100.0 MPa limit


def test_validate_inputs_evaluation_order():
    """REQ-ERR-003: Evaluation order must check P first, then r_i, t, sigma_y."""
    # Both P and t are invalid; P should trigger first
    with pytest.raises(ValueError, match="Pressure must be positive"):
        validate_inputs(-1.0, 500.0, -5.0, 500.0)

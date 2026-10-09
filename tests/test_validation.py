"""Tests for input types, values, ranges, messages and error precedence."""

from fractions import Fraction

import numpy as np
import pytest

from src.errors import ValidationError
from src.validation.inputs import validate_inputs


VALID_INPUTS = {
    "P": 2.0,
    "r_i": 500.0,
    "t": 5.0,
    "sigma_y": 500.0,
}

UNITS = {
    "P": "MPa",
    "r_i": "mm",
    "t": "mm",
    "sigma_y": "MPa",
}


def test_validate_inputs_valid_floats():
    """REQ-TYP-001: Valid inputs return Python floats."""
    result = validate_inputs(**VALID_INPUTS)

    assert result == (2.0, 500.0, 5.0, 500.0)
    assert all(type(value) is float for value in result)


@pytest.mark.parametrize(
    "pressure",
    [
        2,
        2.0,
        np.int64(2),
        np.float32(2),
        np.float64(2),
        Fraction(2, 1),
    ],
)
def test_validate_inputs_supported_real_scalars(pressure):
    """REQ-TYP-001: Supported real scalar types are converted to floats."""
    inputs = {**VALID_INPUTS, "P": pressure}

    result = validate_inputs(**inputs)

    assert result == (2.0, 500.0, 5.0, 500.0)
    assert all(type(value) is float for value in result)


@pytest.mark.parametrize("field", list(VALID_INPUTS))
@pytest.mark.parametrize(
    "bad_value",
    [
        True,
        np.bool_(False),
        "5.0",
        None,
        [5.0],
        {"value": 5.0},
        3 + 4j,
        np.array(5.0),
    ],
)
def test_validate_inputs_rejects_invalid_types(field, bad_value):
    """REQ-TYP-002, REQ-TYP-003, REQ-TYP-004: Reject unsupported inputs."""
    inputs = {**VALID_INPUTS, field: bad_value}

    with pytest.raises(TypeError) as exc_info:
        validate_inputs(**inputs)

    message = str(exc_info.value)

    assert f"({field})" in message
    assert repr(bad_value) in message
    assert UNITS[field] in message
    assert "real numeric scalar" in message


@pytest.mark.parametrize("field", list(VALID_INPUTS))
@pytest.mark.parametrize(
    "bad_value",
    [float("nan"), float("inf"), float("-inf")],
)
def test_validate_inputs_rejects_non_finite(field, bad_value):
    """REQ-VAL-001, REQ-ERR-004: Reject non-finite values with context."""
    inputs = {**VALID_INPUTS, field: bad_value}

    with pytest.raises(ValueError) as exc_info:
        validate_inputs(**inputs)

    message = str(exc_info.value)

    assert f"({field})" in message
    assert repr(bad_value) in message
    assert UNITS[field] in message
    assert "must be finite" in message


@pytest.mark.parametrize("field", list(VALID_INPUTS))
@pytest.mark.parametrize("bad_value", [0.0, -1.0])
def test_validate_inputs_rejects_non_positive(field, bad_value):
    """REQ-VAL-002..005, REQ-ERR-004: Reject zero and negative inputs."""
    inputs = {**VALID_INPUTS, field: bad_value}

    with pytest.raises(ValueError) as exc_info:
        validate_inputs(**inputs)

    message = str(exc_info.value)

    assert f"({field})" in message
    assert repr(bad_value) in message
    assert UNITS[field] in message
    assert "must be positive" in message


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("P", 100.1),
        ("r_i", 0.5),
        ("r_i", 5000.1),
        ("t", 0.01),
        ("t", 500.1),
        ("sigma_y", 9.0),
        ("sigma_y", 3000.1),
    ],
)
def test_validate_inputs_rejects_out_of_range(field, bad_value):
    """REQ-INP-001..004, REQ-VAL-006: Enforce configured input bounds."""
    inputs = {**VALID_INPUTS, field: bad_value}

    with pytest.raises(ValidationError) as exc_info:
        validate_inputs(**inputs)

    message = str(exc_info.value)

    assert f"({field})" in message
    assert repr(bad_value) in message
    assert UNITS[field] in message
    assert "out of range" in message


@pytest.mark.parametrize(
    "values",
    [
        (0.1, 1.0, 0.05, 10.0),
        (100.0, 5000.0, 500.0, 3000.0),
    ],
)
def test_validate_inputs_accepts_range_boundaries(values):
    """REQ-INP-001..004: Accept valid inclusive input boundaries."""
    assert validate_inputs(*values) == values


@pytest.mark.parametrize(
    "overrides,error,expected_field,expected_text",
    [
        (
            {"P": -1.0, "sigma_y": "bad"},
            TypeError,
            "sigma_y",
            "real numeric scalar",
        ),
        (
            {"P": "bad", "r_i": True},
            TypeError,
            "P",
            "real numeric scalar",
        ),
        (
            {"P": -1.0, "t": float("nan")},
            ValueError,
            "t",
            "must be finite",
        ),
        (
            {"P": -1.0, "t": -5.0},
            ValueError,
            "P",
            "must be positive",
        ),
        (
            {"P": 150.0, "r_i": 6000.0},
            ValidationError,
            "P",
            "out of range",
        ),
    ],
)
def test_validate_inputs_error_precedence(
    overrides, error, expected_field, expected_text
):
    """REQ-ERR-002, REQ-ERR-003: Apply stage and parameter precedence."""
    inputs = {**VALID_INPUTS, **overrides}

    with pytest.raises(error) as exc_info:
        validate_inputs(**inputs)

    message = str(exc_info.value)

    assert f"({expected_field})" in message
    assert expected_text in message


def test_validate_inputs_rejects_float_conversion_overflow():
    """REQ-VAL-001: An unrepresentable real input raises a clear error."""
    inputs = {**VALID_INPUTS, "P": 10**400}

    with pytest.raises(ValueError, match="finite and representable"):
        validate_inputs(**inputs)
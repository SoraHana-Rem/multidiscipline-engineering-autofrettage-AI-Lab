"""Validated failure criteria and yield safety-factor calculations."""

import math
from numbers import Real


def _finite_real(name, value):
    """REQ-TYP-001..004, REQ-VAL-001: Require a finite real scalar."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(
            f"{name} must be a real numeric scalar: "
            f"got {value!r} MPa"
        )

    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(
            f"{name} must be finite and representable: "
            f"got {value!r} MPa"
        ) from exc

    if not math.isfinite(number):
        raise ValueError(
            f"{name} must be finite: got {value!r} MPa"
        )

    return number


def _finite_result(value):
    """REQ-ERR-005: Reject non-finite calculated results."""
    if not math.isfinite(value):
        raise ArithmeticError(
            "Non-finite numerical result encountered during computation."
        )

    return value


def safety_factor(sigma_y: float, sigma_vm: float) -> float:
    """
    REQ-FUN-004: Calculate yield strength / equivalent stress.

    Yield strength must be finite and positive.
    Equivalent stress must be finite and non-negative.

    Exactly zero stress raises ZeroDivisionError.
    Tiny positive stresses are accepted when the resulting SF is finite.
    No near-zero cutoff is applied.
    """
    sy = _finite_real("sigma_y", sigma_y)
    seq = _finite_real("sigma_vm", sigma_vm)

    if sy <= 0:
        raise ValueError(
            f"sigma_y must be positive: got {sy} MPa"
        )

    if seq < 0:
        raise ValueError(
            f"sigma_vm cannot be negative: got {seq} MPa"
        )

    if seq == 0:
        raise ZeroDivisionError(
            "Equivalent stress cannot be zero."
        )

    return _finite_result(sy / seq)


def von_mises_plane(sigma_1: float, sigma_2: float) -> float:
    """
    REQ-FUN-004: Evaluate plane-stress von Mises using a stable norm.

    Algebraically equivalent to sqrt(s1² - s1*s2 + s2²).
    Signed stress components are supported.
    """
    s1 = _finite_real("sigma_1", sigma_1)
    s2 = _finite_real("sigma_2", sigma_2)

    result = math.hypot(
        s1 - 0.5 * s2,
        (math.sqrt(3) / 2) * s2,
    )

    return _finite_result(result)


def von_mises_triaxial(
    sigma_1: float,
    sigma_2: float,
    sigma_3: float,
) -> float:
    """
    REQ-FUN-004: Evaluate triaxial von Mises using a stable norm.

    Algebraically equivalent to the existing principal-stress formula.
    Signed stress components are supported.
    """
    s1 = _finite_real("sigma_1", sigma_1)
    s2 = _finite_real("sigma_2", sigma_2)
    s3 = _finite_real("sigma_3", sigma_3)

    result = math.hypot(
        s1 - s2,
        s2 - s3,
        s3 - s1,
    ) / math.sqrt(2)

    return _finite_result(result)
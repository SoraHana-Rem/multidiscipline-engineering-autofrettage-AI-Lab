# Requirements Specification: Pressure Vessel Calculation Module

| Field | Value |
| :--- | :--- |
| Document | `docs/requirements.md` |
| Status | Finalized for Baseline / Capstone Template |
| Related | `docs/design.md`, `docs/assumptions.md` |

Requirement IDs (`REQ-…`) are stable. Every `pytest` test MUST reference at least one ID in its docstring or marker (see `docs/assumptions.md`, rule AI-3).

## 1. System Overview

This module calculates the stress state of a closed-end cylindrical pressure vessel under static internal pressure. It returns hoop stress, longitudinal stress, radial stress, the von Mises equivalent stress, and a yield safety factor, to support baseline structural integrity analysis.

Two analytical models are used, selected automatically from the geometry (Hearn, Vol. 1, Ch. 10):

* **Thin-wall model** for $r_i / t \ge 10$.
* **Thick-wall (Lamé) model** for $r_i / t < 10$.

**Units (fixed, no conversion inside the module):** pressure and stress in MPa, lengths in mm.

## 2. Input Specifications & Validation Guardrails

All inputs MUST be validated **before** any stress equation executes. Validation is all-or-nothing: the first failing check halts execution and no partial result is returned.

### 2.1 Input parameters

| ID | Parameter | Identifier | Unit | Accepted type | Allowed range (inclusive) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| REQ-INP-001 | Internal pressure | `P` | MPa | `int` or `float` | $0 < P \le 100$ |
| REQ-INP-002 | Inner radius | `r_i` | mm | `int` or `float` | $1 \le r_i \le 5000$ |
| REQ-INP-003 | Wall thickness | `t` | mm | `int` or `float` | $0.05 \le t \le 500$ |
| REQ-INP-004 | Yield strength | `sigma_y` | MPa | `int` or `float` | $10 \le \sigma_y \le 3000$ |

> Bounds are stored in a single configuration module (`src/config/limits.py`).

### 2.2 Type validation rules

| ID | Rule | Error raised |
| :--- | :--- | :--- |
| REQ-TYP-001 | Accepted types are `int` and `float` (any `numbers.Real`, including NumPy real scalars). Integers are converted to `float` internally. | — |
| REQ-TYP-002 | `bool` MUST be rejected, even though it is a subclass of `int` in Python. | `TypeError` |
| REQ-TYP-003 | `None`, `str`, `complex`, sequences, and arrays MUST be rejected. | `TypeError` |
| REQ-TYP-004 | Strings MUST NOT be coerced (`"5.0"` is invalid). | `TypeError` |

### 2.3 Value validation and error handling

| ID | Condition | Error raised | Message template |
| :--- | :--- | :--- | :--- |
| REQ-VAL-001 | Value is `NaN` or $\pm\infty$ | `ValueError` | `"<Name> must be finite: got <value>"` |
| REQ-VAL-002 | `P <= 0` | `ValueError` | `"Pressure must be positive: got <value> MPa"` |
| REQ-VAL-003 | `r_i <= 0` | `ValueError` | `"Inner radius must be positive: got <value> mm"` |
| REQ-VAL-004 | `t <= 0` | `ValueError` | `"Wall thickness must be positive: got <value> mm"` |
| REQ-VAL-005 | `sigma_y <= 0` | `ValueError` | `"Yield strength must be positive: got <value> MPa"` |
| REQ-VAL-006 | Any value outside its range in §2.1 (but not caught above) | `ValueError` | `"<Name> out of range [<min>, <max>] <unit>: got <value>"` |

Error-handling rules:

* **REQ-ERR-001:** The module MUST NOT silently clamp, round, default, or "fix" an invalid input.
* **REQ-ERR-002:** Type checks run before value checks; a `TypeError` takes precedence over a `ValueError`.
* **REQ-ERR-003:** When several inputs are invalid, the module reports the first failure in the order `P`, `r_i`, `t`, `sigma_y`.
* **REQ-ERR-004:** Error messages MUST contain the parameter name, the offending value, and the unit.
* **REQ-ERR-005:** Calculation functions MUST NOT emit `NaN` or `inf`. If a result is non-finite, raise `ArithmeticError` rather than return it.

## 3. Functional Requirements

### 3.1 Model selection

| ID | Requirement |
| :--- | :--- |
| REQ-FUN-001 | The module computes the ratio $r_i / t$ and selects the model. $r_i / t \ge 10$ selects thin-wall; $r_i / t < 10$ selects thick-wall (Hearn, Vol. 1, Ch. 10). |
| REQ-FUN-002 | When thick-wall is selected, the module MUST emit a `PressureVesselWarning` (subclass of `UserWarning`). |
| REQ-FUN-003 | The result MUST report which model was used (`"thin_wall"` or `"lame_thick_wall"`). |

### 3.2 Governing equations (Tension positive, external pressure = 0)

**Thin-wall model** (uses inner radius $r_i$; radial stress is neglected, $\sigma_r = 0$; Hearn, Vol. 1, Ch. 9):

$$\sigma_\theta = \frac{P\,r_i}{t}, \qquad \sigma_L = \frac{P\,r_i}{2t}, \qquad \sigma_r = 0$$

$$\sigma_{vm} = \sqrt{\sigma_\theta^2 - \sigma_\theta\,\sigma_L + \sigma_L^2}$$

**Thick-wall Lamé model** with $a = r_i$, $b = r_i + t$, evaluated at the inner surface ($r = a$) where stress is maximum (Hearn, Vol. 1, Ch. 10):

$$\sigma_\theta = P\,\frac{b^2 + a^2}{b^2 - a^2}, \qquad \sigma_L = P\,\frac{a^2}{b^2 - a^2}, \qquad \sigma_r = -P$$

$$\sigma_{vm} = \sqrt{\tfrac{1}{2}\left[(\sigma_\theta - \sigma_r)^2 + (\sigma_r - \sigma_L)^2 + (\sigma_L - \sigma_\theta)^2\right]}$$

**Yield criteria (Distortion Energy / von Mises; Hearn, Vol. 1, Ch. 15):**

$$SF = \frac{\sigma_y}{\sigma_{vm}}$$

| ID | Requirement |
| :--- | :--- |
| REQ-FUN-004 | The module returns `sigma_hoop`, `sigma_long`, `sigma_radial`, `sigma_vm`, `safety_factor`, `yielded`, and `model`. |
| REQ-FUN-005 | `yielded` is `True` when $\sigma_{vm} \ge \sigma_y$ ($SF \le 1$). Yielding is a reported *result*, not an error. |
| REQ-FUN-006 | The equations above are fixed. They MUST NOT be changed without explicit approval (see `docs/assumptions.md`, rule AI-1). |

## 4. Performance & Precision Acceptance Criteria

### 4.1 Numerical precision

| ID | Criterion |
| :--- | :--- |
| REQ-PRC-001 | Every stress output (MPa) matches analytical reference values within an **absolute tolerance of $\pm 10^{-4}$ MPa**. |
| REQ-PRC-002 | `safety_factor` matches its reference within an absolute tolerance of $\pm 10^{-4}$. |
| REQ-PRC-003 | Calculations use IEEE-754 double precision (`float`). |
| REQ-PRC-004 | Results are deterministic: identical inputs yield bit-identical outputs. |

### 4.2 Boundary guardrails

| ID | Criterion |
| :--- | :--- |
| REQ-BND-001 | $r_i / t = 10$ exactly selects the **thin-wall** model. |
| REQ-BND-002 | Ratios strictly below 10 select the **thick-wall** model and emit the warning from REQ-FUN-002. |
| REQ-BND-003 | Values exactly on range limits in §2.1 are accepted; values outside are rejected. |

## 5. Acceptance Criteria

### 5.1 Reference test vectors

| Case | `P` (MPa) | `r_i` (mm) | `t` (mm) | `sigma_y` (MPa) | Model | $\sigma_\theta$ | $\sigma_L$ | $\sigma_r$ | $\sigma_{vm}$ | $SF$ |
| :--- | ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: |
| TV-1 (thin) | 2.0 | 500 | 5 | 500 | thin_wall | 200.0000 | 100.0000 | 0 | 173.2051 | 2.8868 |
| TV-2 (thick) | 1.0 | 10 | 10 | 250 | lame_thick_wall | 1.6667 | 0.3333 | −1.0000 | 2.3094 | 108.2532 |
| TV-3 (yield) | 10.0 | 500 | 5 | 500 | thin_wall | 1000.0000 | 500.0000 | 0 | 866.0254 | 0.5774 |

`yielded` is `False` for TV-1 and TV-2, and `True` for TV-3.

## 6. Out of Scope

Effects listed in `docs/assumptions.md` §1 as excluded (external pressure, thermal loads, fatigue, composite structures, buckling, and autofrettage yield prestress [Hearn, Vol. 2]) are out of scope for this baseline module.
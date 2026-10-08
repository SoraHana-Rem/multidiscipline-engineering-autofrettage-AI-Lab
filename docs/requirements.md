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
| REQ-TYP-001 | Accept scalar instances of `numbers.Real`, including Python `int`/`float` and supported NumPy integer/floating scalars. Valid inputs are converted to Python `float`. | — |
| REQ-TYP-002 | Reject Python and NumPy booleans. | `TypeError` |
| REQ-TYP-003 | Reject `None`, strings, complex numbers, collections and arrays, including zero-dimensional arrays. | `TypeError` |
| REQ-TYP-004 | Do not coerce strings to numbers. `"5.0"` is invalid. | `TypeError` |

### 2.3 Value validation and error handling

| ID | Condition | Error raised |
| :--- | :--- | :--- |
| REQ-VAL-001 | A real input is non-finite or cannot be represented as a finite Python float. | `ValueError` |
| REQ-VAL-002 | `P <= 0` | `ValueError` |
| REQ-VAL-003 | `r_i <= 0` | `ValueError` |
| REQ-VAL-004 | `t <= 0` | `ValueError` |
| REQ-VAL-005 | `sigma_y <= 0` | `ValueError` |
| REQ-VAL-006 | A positive finite input lies outside its configured range in §2.1. | `ValidationError`, a subclass of `ValueError` |

Error-handling rules:

- **REQ-ERR-001:** Do not silently clamp, round, default or repair invalid
  inputs. Conversion of accepted real scalars to Python float follows
  REQ-TYP-001.
- **REQ-ERR-002:** Validation stages run in this order: type, finiteness,
  positivity, range. Complete each stage across all inputs before
  proceeding to the next. Type errors therefore precede value errors.
- **REQ-ERR-003:** Within each validation stage, check parameters in the
  order `P`, `r_i`, `t`, `sigma_y`. Report the first failure in the
  earliest failing stage.
- **REQ-ERR-004:** Input-validation messages contain the descriptive
  parameter name, identifier, offending value and expected unit.
  Type messages also identify the supplied type.
- **REQ-ERR-005:** Calculation results must not contain `NaN` or `inf`.
  Raise `ArithmeticError` if a computed result is non-finite.

Message forms:

- Type: `<Name> (<identifier>) must be a real numeric scalar:
  got <value> <unit>; type=<type>`
- Finiteness: `<Name> (<identifier>) must be finite:
  got <value> <unit>`
- Positivity: `<Name> must be positive (<identifier>):
  got <value> <unit>`
- Range: `<Name> out of range (<identifier>):
  expected [<min>, <max>] <unit>; got <value> <unit>`

A finite real value that overflows Python-float conversion receives
a message identifying the finite-representability failure.

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

### 3.3 Autofrettage extension (`src/physics/autofrettage.py`)

Autofrettage is a separate, optional extension layered on top of the baseline module in §3.1–3.2, not a replacement for it. `analyze_vessel` (the baseline path) never includes autofrettage effects; it is only invoked when the caller explicitly requests it (CLI flag `--autofrettage-pressure`).

| ID | Requirement |
| :--- | :--- |
| REQ-AUT-001 | Given an autofrettage pressure $P_{auto}$, inner/outer radius, and $\sigma_y$, the module computes the elastic-plastic boundary radius $r_p$ (Hearn, Vol. 2). |
| REQ-AUT-002 | $P_{auto}$ MUST lie strictly between the initial-yield pressure and the full-yield pressure of the cylinder; outside that range the module raises `ValidationError` rather than extrapolating. |
| REQ-AUT-003 | The module computes the residual hoop stress at the bore after elastic unload from $P_{auto}$ (purely elastic unloading assumed; no Bauschinger effect, see `docs/assumptions.md` A-AUT-03). |
| REQ-AUT-004 | When a positive working pressure is supplied, the module reports a bore-only von Mises yield safety-factor estimate. The calculation superimposes residual hoop stress on the elastic working-pressure hoop stress, uses working-pressure radial and closed-end axial stresses, and omits residual axial stress. It does not establish the minimum safety factor across the wall or guarantee improvement over the baseline. When working pressure is omitted, `safety_factor` is `None`. |


Autofrettage input contract:

    Pressure, radii and yield strength accept real numeric scalars;
    booleans and strings are rejected.
    Supplied scalar values must be finite and positive.
    The outer radius must exceed the inner radius.
    Autofrettage pressure must be strictly above initial yield and
    strictly below full yield.
    Profile point count must be an integer of at least two.
    When supplied, working pressure must be finite and positive.
    When working pressure is omitted, residual stresses are calculated
    and safety_factor is None, meaning not calculated.

## 4. Performance & Precision Acceptance Criteria

### 4.1 Numerical precision

| ID | Criterion |
| :--- | :--- |
| REQ-PRC-001 | Every stress output (MPa) matches analytical reference values within an **absolute tolerance of $\pm 10^{-4}$ MPa**. |
| REQ-PRC-002 | `safety_factor` matches its reference within an absolute tolerance of $\pm 10^{-4}$. |
| REQ-PRC-003 | Calculations use IEEE-754 double precision (`float`). |
| REQ-PRC-004 | Results are deterministic: identical inputs yield bit-identical outputs. |

#### Failure-helper numerical policy

The public functions in `src/physics/failure.py` accept finite real
numeric scalars and reject booleans, strings and non-finite inputs.

For `safety_factor`, yield strength must be positive and equivalent
stress must be non-negative. Exactly zero equivalent stress raises
`ZeroDivisionError`. Positive equivalent stress has no arbitrary
near-zero cutoff; a non-finite calculated safety factor raises
`ArithmeticError`.

The baseline pressure contract remains `0 < P <= 100 MPa`.
Very small positive pressures are supported when calculations remain
representable and the returned results are finite.

The von Mises functions accept signed stress components. They use
algebraically equivalent norm formulations to reduce intermediate
overflow and underflow.

### 4.2 Boundary guardrails

| ID | Criterion |
| :--- | :--- |
| REQ-BND-001 | `r_i / t = 10` exactly selects the thin-wall model without emitting `PressureVesselWarning`. |
| REQ-BND-002 | Ratios strictly below 10 select the thick-wall Lamé model and emit `PressureVesselWarning`. |
| REQ-BND-003 | Reject inputs outside the configured numerical bounds, including the documented examples of unit slips that produce out-of-range values. Inputs contain no unit metadata, so unit mistakes that remain within the bounds cannot be detected automatically. |
# System Architecture & Design: Pressure Vessel Module

| Field | Value |
| :--- | :--- |
| Document | `docs/design.md` |
| Status | Finalized for Baseline / Capstone Template |
| Related | `docs/requirements.md`, `docs/assumptions.md` |

## 1. Design Goals

* **Separation of concerns:** validation, calculation, orchestration, and tests are separate layers with one-way dependencies.
* **Pure physics:** calculation code has no I/O, no global state, no input validation, and no hard-coded limits or tolerances (these come from `src/config/limits.py`).
* **Fail fast:** invalid input is rejected before any equation runs, and no partial results are returned.
* **Traceability:** each test maps to a requirement ID in `docs/requirements.md`.

## 2. Directory Structure

```text
multidiscipline-engineering-autofrettage/
├── docs/                     # requirements, design, assumptions, reference, checklists, audits
├── src/
│   ├── __init__.py
│   ├── main.py               # CLI entry point (argparse), result formatting
│   ├── analysis.py           # orchestrator: analyze_vessel(...) -> VesselResult
│   ├── errors.py             # PressureVesselWarning, ValidationError
│   ├── config/
│   │   └── limits.py         # numeric limits, ratio threshold, tolerances (single source of truth)
│   ├── validation/
│   │   ├── inputs.py         # type + finite + positive + range checks
│   │   └── cross_validate.py # MATLAB-vs-Python comparison runner
│   └── physics/
│       ├── thin_wall.py      # hoop / longitudinal stress (Hearn Vol. 1 Ch. 9)
│       ├── thick_wall.py     # Lamé equations (Hearn Vol. 1 Ch. 10)
│       ├── failure.py        # von Mises, safety factor (Hearn Vol. 1 Ch. 15)
│       └── autofrettage.py   # plastic radius, residual stress (extension, Hearn Vol. 2)
├── tests/
│   ├── conftest.py           # shared fixtures, reference test vectors TV-1..TV-3
│   ├── test_validation.py
│   ├── test_physics.py
│   ├── test_analysis.py      # end-to-end and model-selection tests
│   ├── test_autofrettage.py
│   ├── test_config.py
│   ├── test_cross_validation.py
│   └── test_main.py          # CLI pipeline
├── python/                   # standalone Lamé solver + plotting (independent cross-check engine)
├── matlab/                   # MATLAB reference engine
├── agents/                   # workspace audit scripts
├── evaluation/, prompts/     # LLM benchmark and prompt artifacts
├── output/plots/             # generated figures
└── pytest.ini                # pytest configuration
```

`python_basics/` contains personal Python-learning scratch files and is not part of the module.

## 3. Module Boundaries

| Layer | Path | Responsibility | May import | Must NOT |
| :--- | :--- | :--- | :--- | :--- |
| Config | `src/config/` | Numeric limits, thin/thick threshold, tolerances. | nothing | contain logic |
| Validation | `src/validation/inputs.py` | Checks type, finiteness, positivity, and range of raw inputs. | config, errors | compute stresses |
| Physics core | `src/physics/` | Pure functions turning valid floats into stresses. | `math`, `numpy`, `scipy` (autofrettage only), config (tolerances only), errors (autofrettage only) | validate raw input types, do I/O, emit warnings |
| Orchestrator | `src/analysis.py` | Validates, selects model, executes physics, emits warnings. | config, validation, physics, errors | contain equations |
| CLI | `src/main.py` | Parses arguments, calls orchestrator and autofrettage, prints results. | analysis, physics.autofrettage | contain equations |
| Tests | `tests/` | Verify every requirement. | everything under `src/` | be imported by `src/` |

**Numerical policy:** the failure helpers use exact-zero handling
rather than a configurable near-zero stress cutoff. Public failure
helpers validate real scalar types and finiteness; `safety_factor`
also checks strength and equivalent-stress signs. Non-finite computed
results raise `ArithmeticError`. Input bounds and the model-selection
threshold remain in `src/config/limits.py`.

Dependency rule (one-way):

```text
tests ──► main ──► analysis ──► validation ──► config
                       │
                       ├──► physics ──► config
                       └──► config
(errors.py is imported by validation, analysis and physics.autofrettage)
```

## 4. Data Flow (baseline path)

```text
                    raw inputs: P, r_i, t, sigma_y
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │  analysis.analyze_vessel  │
                    └─────────────┬─────────────┘
                                  │ 1. validate
                                  ▼
                    ┌───────────────────────────┐
                    │  validation.inputs        │──► TypeError / ValueError
                    │  (type → finite → range)  │    (halt, no result)
                    └─────────────┬─────────────┘
                                  │ validated floats
                                  │ 2. compute ratio = r_i / t
                                  ▼
                        ┌───────────────────┐
                        │  ratio >= 10 ?    │  (threshold from config)
                        └────┬─────────┬────┘
                         yes │         │ no
                             ▼         ▼
                  ┌────────────────┐ ┌───────────────────────────┐
                  │ physics.       │ │ warn PressureVesselWarning│
                  │ thin_wall      │ │ physics.thick_wall (Lamé) │
                  └───────┬────────┘ └─────────────┬─────────────┘
                          └────────────┬───────────┘
                                       │ sigma_hoop, sigma_long, sigma_radial
                                       │ 3. failure criterion
                                       ▼
                             ┌───────────────────┐
                             │ physics.failure   │
                             │ von Mises, SF     │
                             └─────────┬─────────┘
                                       │ 4. finite-result check
                                       ▼
                             ┌───────────────────┐
                             │  VesselResult     │──► ArithmeticError if any
                             │ (frozen dataclass)│    value is NaN / inf
                             └───────────────────┘
```

**Autofrettage branch:** when requested, `main.run_pipeline` calls
`physics.autofrettage.calculate_autofrettage(...)`. This returns the
plastic radius, bore residual hoop stress, and an optional bore-only
working safety-factor estimate. The estimate uses residual-hoop
superposition, omits residual axial stress, and assumes elastic
reloading. It does not determine the minimum safety factor across
the wall.

## 5. Public Interfaces

### 5.1 Orchestrator

```python
@dataclass(frozen=True)
class VesselResult:
    sigma_hoop: float      # MPa
    sigma_long: float      # MPa
    sigma_radial: float    # MPa
    sigma_vm: float        # MPa
    safety_factor: float   # dimensionless
    yielded: bool
    model: str             # "thin_wall" | "lame_thick_wall"

def analyze_vessel(P: float, r_i: float, t: float, sigma_y: float) -> VesselResult: ...
```

### 5.2 Validation

```python
def validate_inputs(P, r_i, t, sigma_y) -> tuple[float, float, float, float]: ...
```

### 5.3 Physics core (pure, all take and return floats unless stated)

```python
# thin_wall.py
def calculate_thin_wall_stress(P: float, r_i: float, t: float) -> float: ...   # hoop
def longitudinal_stress(P: float, r_i: float, t: float) -> float: ...

# thick_wall.py
def calculate_thick_wall_stress(P: float, r_i: float, t: float) -> float: ...  # hoop at bore
def lame_stresses_inner(P: float, r_i: float, t: float) -> tuple[float, float, float]: ...

# failure.py
def von_mises_plane(sigma_1: float, sigma_2: float) -> float: ...
def von_mises_triaxial(sigma_1: float, sigma_2: float, sigma_3: float) -> float: ...
def safety_factor(sigma_y: float, sigma_vm: float) -> float: ...

# autofrettage.py (extension)
def calculate_plastic_radius(P_auto: float, r_i: float, r_o: float, sigma_y: float) -> float: ...
def calculate_autofrettage_stresses(P_auto, r_i, r_o, sigma_y, num_points: int = 100) -> dict: ...
def calculate_autofrettage(P_auto, r_i, r_o, sigma_y, P_working=None) -> AutofrettageResult: ...
# AutofrettageResult: r_p, residual_hoop_inner, safety_factor
```

### 5.4 CLI

```python
def run_pipeline(P, r_i, t, sigma_y, P_auto=None, json_output: bool = False) -> None: ...
```

## 6. Error Handling Strategy

**Numerical policy:** the failure helpers use exact-zero handling
rather than a configurable near-zero stress cutoff. Public failure
helpers validate real scalar types and finiteness; `safety_factor`
also checks strength and equivalent-stress signs. Non-finite computed
results raise `ArithmeticError`. Input bounds and the model-selection
threshold remain in `src/config/limits.py`.
* **No swallowing inside the module.** Only the outermost CLI (`main.run_pipeline`) catches `ValueError`, `TypeError` and `ArithmeticError`, to print a clean message and exit with status 1.
* **Ordered checks.** Type → Finiteness → Positivity → Range. Parameters are evaluated in the order P, r_i, t, sigma_y.
* **Exception types.** `TypeError` (bad type), `ValueError` (bad value), `ValidationError` (a `ValueError` subclass for range and autofrettage-applicability failures), `ZeroDivisionError` and `ArithmeticError` (zero or non-finite stress).
* **Yielding is a result.** `yielded=True` is returned normally without throwing exceptions.

## 7. Requirement Tagging Convention

Every function in `src/` and every test in `tests/` cites at least one `REQ-` ID from `docs/requirements.md` in its docstring, for example `"""REQ-FUN-004, REQ-PRC-002: ..."""`.

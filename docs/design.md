# System Architecture & Design: Pressure Vessel Module

| Field | Value |
| :--- | :--- |
| Document | `docs/design.md` |
| Scope | Baseline pressure-vessel analysis and optional autofrettage extension |
| Related | `docs/requirements.md`, `docs/assumptions.md` |

## 1. Design Goals

- **Separation of concerns:** input validation, physics calculations, orchestration, presentation and verification have separate responsibilities.
- **Calculation functions without I/O:** physics functions calculate results without reading files, printing output or generating plots. Public failure and autofrettage helpers also validate their own input contracts.
- **Fail fast:** rejected inputs halt calculation rather than being silently repaired.
- **Central baseline configuration:** vessel input bounds and the thin-wall selection threshold are defined in `src/config/limits.py`.
- **Traceability:** requirement IDs connect specified behaviour to implementation and tests. Tagging is a project convention; complete coverage is not currently enforced automatically.

Units are MPa for pressure and stress, and mm for geometry.
Safety factors are dimensionless.

## 2. Repository Structure

| Path | Purpose |
| :--- | :--- |
| `src/main.py` | CLI argument parsing, calculation calls and result formatting |
| `src/analysis.py` | Baseline analysis orchestration and `VesselResult` |
| `src/errors.py` | `ValidationError` and `PressureVesselWarning` |
| `src/config/limits.py` | Baseline input bounds and model-selection threshold |
| `src/validation/inputs.py` | Type, finiteness, positivity and range validation |
| `src/validation/cross_validate.py` | Comparison against MATLAB reference data |
| `src/validation/matlab_reference.csv` | MATLAB reference dataset |
| `src/validation/matlab-python-comparison.md` | Comparison documentation |
| `src/physics/thin_wall.py` | Thin-wall hoop and longitudinal stresses |
| `src/physics/thick_wall.py` | Lamé stresses at the bore |
| `src/physics/failure.py` | Validated von Mises and safety-factor helpers |
| `src/physics/autofrettage.py` | Extension validation, plastic radius and residual stresses |
| `src/visualization/plots.py` | Residual-hoop-stress plotting from solver results |
| `tests/conftest.py` | Shared fixtures and reference vectors |
| `tests/test_validation.py` | Baseline input contracts and error precedence |
| `tests/test_physics.py` | Physics helpers and numerical edge cases |
| `tests/test_analysis.py` | Baseline integration and model selection |
| `tests/test_autofrettage.py` | Autofrettage calculations and input boundaries |
| `tests/test_config.py` | Configuration checks |
| `tests/test_cross_validation.py` | Reference-comparison behaviour |
| `tests/test_main.py` | CLI output and error handling |
| `tests/test_plots.py` | Plot data and plastic-boundary verification |
| `tests/test_audit_heuristics.py` | Audit text-scan behaviour and report wording |
| `agents/` | Heuristic repository scan and report generator |
| `matlab/` | MATLAB calculation and reference-export scripts |
| `docs/` | Requirements, design, assumptions, references and audit documents |
| `evaluation/` | Benchmark cases and captured verification evidence |
| `prompts/` | Prompt experiments |
| `learning/python_basics/` | Python learning exercises |
| `learning/week09-11-draft/` | Earlier exploratory calculation scripts |
| `.github/skills/` | Engineering-review skill |
| `.github/workflows/main.yml` | CI test and coverage workflow |
| `output/` | Existing generated/reference output files |
| `outputs/` | Default destination for the residual-stress plot |
| `pytest.ini` | Test discovery and project-path configuration |
| `requirements.txt` | Python dependencies |

`src/` is the application package. Files under `learning/` are earlier
exercises and drafts, not part of the baseline application or evidence
of independent numerical validation.

## 3. Module Boundaries

| Component | Responsibility | Dependencies | Boundary |
| :--- | :--- | :--- | :--- |
| Configuration | Baseline bounds and model threshold | No application imports | Contains constants rather than calculation logic |
| Input validation | Validate raw vessel inputs and return Python floats | Configuration, errors, standard library | Does not calculate stresses |
| Thin/thick-wall physics | Calculate elastic stresses | Standard library as required | No file I/O, plotting or warning emission |
| Failure helpers | Validate stress scalars; calculate von Mises stress and SF | `math`, `numbers.Real` | No vessel-range enforcement or I/O |
| Autofrettage | Validate extension inputs; calculate loading and residual stresses | `math`, NumPy, SciPy, errors | No CLI output or plotting |
| Baseline orchestrator | Validate, select model, calculate results and emit model warnings | Configuration, validation, physics, errors | Does not implement stress equations |
| CLI | Parse inputs, call calculations and format output | Analysis and autofrettage | Does not implement stress equations |
| Visualization | Plot arrays and plastic radius supplied by the solver | Autofrettage, Matplotlib, filesystem utilities | Does not duplicate solver equations |
| Cross-validation | Load reference data and compare numerical results | NumPy, pandas, filesystem utilities | Separate verification path |
| Audit tooling | Search selected file text and report matches/read failures | Standard library | Does not establish engineering correctness |
| Tests | Exercise application and tooling behaviour | Application, agents, pytest | Application code does not import tests |

Baseline dependencies run from CLI to orchestration, then validation
and physics. Validation uses configuration and shared errors.

The CLI invokes autofrettage separately when requested. Visualization
calls the autofrettage solver directly. Cross-validation and audit
tooling have their own verification/reporting responsibilities.

## 4. Baseline Data Flow

| Stage | Behaviour |
| :--- | :--- |
| 1. Validate | `validate_inputs(P, r_i, t, sigma_y)` checks type, finiteness, positivity and range, then returns Python floats |
| 2. Select model | Calculate `r_i / t`; ratios at least 10 select thin-wall, smaller ratios select Lamé |
| 3. Calculate stresses | Return hoop, longitudinal and radial stresses; thin-wall radial stress is zero |
| 4. Evaluate failure | Calculate von Mises stress, yield safety factor and yielded status |
| 5. Check outputs | Reject non-finite calculated stress or safety-factor values |
| 6. Return result | Construct the frozen `VesselResult` dataclass |

Selecting Lamé emits `PressureVesselWarning` from the orchestrator.

### Autofrettage path

When requested, `main.run_pipeline` calls
`calculate_autofrettage` after baseline analysis.

The extension validates its inputs, determines the plastic radius,
calculates loading stresses and subtracts elastic unloading stresses.

When working pressure is supplied, it returns a bore-only safety-factor
estimate using residual-hoop superposition with working-pressure radial
and closed-end axial stresses.

Residual axial stress is omitted and elastic reloading is assumed.
The estimate does not establish the minimum safety factor across the
wall or guarantee improvement over the baseline.

When working pressure is omitted, residual stresses are calculated
and `safety_factor` is `None`.

## 5. Public Interfaces

### 5.1 Baseline result and orchestrator

```python
@dataclass(frozen=True)
class VesselResult:
    sigma_hoop: float      # MPa
    sigma_long: float      # MPa
    sigma_radial: float    # MPa
    sigma_vm: float        # MPa
    safety_factor: float   # dimensionless
    yielded: bool
    model: str             # "thin_wall" or "lame_thick_wall"

def analyze_vessel(P, r_i, t, sigma_y) -> VesselResult: ...
```

### 5.2 Input validation

```python
def validate_inputs(P, r_i, t, sigma_y): ...
```

Returns four Python floats in the order `P`, `r_i`, `t`, `sigma_y`.

### 5.3 Physics

```python
# thin_wall.py
def calculate_thin_wall_stress(P, r_i, t) -> float: ...
def longitudinal_stress(P, r_i, t) -> float: ...

# thick_wall.py
def calculate_thick_wall_stress(P, r_i, t) -> float: ...
def lame_stresses_inner(P, r_i, t) -> tuple[float, float, float]: ...

# failure.py
def von_mises_plane(sigma_1, sigma_2) -> float: ...
def von_mises_triaxial(sigma_1, sigma_2, sigma_3) -> float: ...
def safety_factor(sigma_y, sigma_vm) -> float: ...

# autofrettage.py
def calculate_plastic_radius(P_auto, r_i, r_o, sigma_y) -> float: ...
def calculate_autofrettage_stresses(
    P_auto, r_i, r_o, sigma_y, num_points=100
) -> dict: ...
def calculate_autofrettage(
    P_auto, r_i, r_o, sigma_y, P_working=None
) -> AutofrettageResult: ...
```

`lame_stresses_inner` returns hoop, longitudinal and radial stresses.

`AutofrettageResult` contains `r_p`, `residual_hoop_inner` and
`safety_factor`. The latter is optional.

### 5.4 CLI

```python
def run_pipeline(
    P, r_i, t, sigma_y, P_auto=None, json_output=False
) -> None: ...
```

### 5.5 Visualization

```python
def generate_residual_stress_plot(
    r_i,
    r_o,
    sigma_y,
    P_auto,
    output_path="outputs/residual_stress.png",
) -> str: ...
```

The plot uses the solver's radius array, residual hoop-stress array and
plastic radius. It returns the saved image path.

## 6. Validation and Error Handling

### Baseline input validation

Validation completes each stage across all four parameters before
moving to the next:

1. Type
2. Finiteness and Python-float representability
3. Positivity
4. Configured range

Within each stage, parameter order is `P`, `r_i`, `t`, `sigma_y`.

Supported real numeric scalars are converted to Python floats.
Booleans, strings, complex values, collections and arrays are rejected.

### Public failure helpers

Failure helpers enforce their own real-scalar and finiteness contracts.
The von Mises helpers accept signed stress components.

For `safety_factor`:

- Yield strength must be positive.
- Equivalent stress must be non-negative.
- Exactly zero equivalent stress raises `ZeroDivisionError`.
- Tiny positive equivalent stress has no arbitrary near-zero cutoff.
- A non-finite calculated safety factor raises `ArithmeticError`.

The von Mises helpers use algebraically equivalent norm formulations
to reduce intermediate overflow and underflow.

### Autofrettage validation

Autofrettage entry points validate their extension inputs separately:

- Supplied pressure, radii and strength must be finite and positive.
- Outer radius must exceed inner radius.
- Autofrettage pressure must lie strictly between initial and full yield.
- Profile point count must be an integer of at least two.
- Supplied working pressure must be finite and positive.

### Errors and warnings

| Condition | Response |
| :--- | :--- |
| Unsupported baseline/failure-helper input type | `TypeError` |
| Invalid baseline/failure-helper finite value or sign | `ValueError` |
| Baseline range failure | `ValidationError`, a `ValueError` subclass |
| Autofrettage applicability/value failure | `ValidationError` |
| Exactly zero equivalent stress in the SF helper | `ZeroDivisionError` |
| Non-finite calculated baseline/failure-helper result | `ArithmeticError` |
| Thick-wall model selected | `PressureVesselWarning` |
| Predicted baseline yielding | Return `yielded=True`; do not raise an exception |

The CLI catches `ValueError`, `TypeError` and `ArithmeticError`,
prints an execution error and exits with status 1.
Unexpected integration errors propagate.

## 7. Requirement Tagging Convention

The project requires requirement references in test docstrings or
markers. Requirement IDs belong to `docs/requirements.md`.

Example:

```python
"""REQ-FUN-004, REQ-PRC-002: Verify the reference analysis result."""
```

Tagging is intended to support traceability. The current implementation
does not automatically enforce complete tagging or demonstrate that
every requirement has verification coverage.
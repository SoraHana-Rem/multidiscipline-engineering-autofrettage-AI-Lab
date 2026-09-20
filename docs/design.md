# System Architecture & Design: Pressure Vessel Module

| Field | Value |
| :--- | :--- |
| Document | `docs/design.md` |
| Status | Finalized for Baseline / Capstone Template |
| Related | `docs/requirements.md`, `docs/assumptions.md` |

## 1. Design Goals

* **Separation of concerns:** validation, calculation, orchestration, and tests are separate layers with one-way dependencies.
* **Pure physics:** calculation code has no I/O, no global state, no configuration constants, and no validation.
* **Fail fast:** invalid input is rejected before any equation runs, and no partial results are returned.
* **Traceability:** each test maps to a requirement ID in `docs/requirements.md`.

## 2. Directory Structure

```text
project_root/
├── docs/
│   ├── requirements.md
│   ├── design.md
│   └── assumptions.md
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── limits.py         # numeric guardrails, ratio threshold (single source of truth)
│   ├── errors.py             # PressureVesselWarning
│   ├── validation/
│   │   ├── __init__.py
│   │   └── inputs.py         # type + range checks; raises TypeError / ValueError
│   ├── physics/
│   │   ├── __init__.py
│   │   ├── thin_wall.py      # hoop / longitudinal stress (thin-wall; Hearn Vol. 1 Ch. 9)
│   │   ├── thick_wall.py     # Lamé equations (thick-wall; Hearn Vol. 1 Ch. 10)
│   │   └── failure.py        # von Mises, safety factor (Hearn Vol. 1 Ch. 15)
│   └── analysis.py           # orchestrator: analyze_vessel(...) -> VesselResult
├── tests/
│   ├── conftest.py           # shared fixtures, reference test vectors TV-1..TV-3
│   ├── test_validation.py
│   ├── test_thin_wall.py
│   ├── test_thick_wall.py
│   ├── test_failure.py
│   └── test_analysis.py      # end-to-end and model-selection tests
└── pyproject.toml            # pytest config, tool settings



3. Module BoundariesLayerPathResponsibilityMay importMust NOTConfigsrc/config/Holds numeric limits and thin/thick threshold.nothingcontain logicValidationsrc/validation/Checks type, finiteness, and range of raw inputs.configcompute stressesPhysics coresrc/physics/Pure functions turning valid floats into stresses.standard library math onlyvalidate, import config, emit warningsOrchestratorsrc/analysis.pyValidates, selects model, executes physics, emits warnings.config, validation, physics, errorscontain equationsTeststests/Verify every requirement.everything under src/be imported by src/Dependency rule (one-way):Plaintexttests ──► analysis ──► validation ──► config
                  └──► physics
                  └──► config
4. Data FlowPlaintext                     raw inputs: P, r_i, t, sigma_y
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
                             │  (frozen dataclass)│    value is NaN / inf
                             └───────────────────┘
5. Public Interfaces5.1 OrchestratorPython@dataclass(frozen=True)
class VesselResult:
    sigma_hoop: float      # MPa
    sigma_long: float      # MPa
    sigma_radial: float    # MPa
    sigma_vm: float        # MPa
    safety_factor: float   # dimensionless
    yielded: bool
    model: str             # "thin_wall" | "lame_thick_wall"

def analyze_vessel(P: float, r_i: float, t: float, sigma_y: float) -> VesselResult: ...
5.2 ValidationPythondef validate_inputs(P: object, r_i: object, t: object, sigma_y: object) -> tuple[float, float, float, float]: ...
5.3 Physics core (all pure, all take and return float)Python# thin_wall.py
def hoop_stress(P: float, r_i: float, t: float) -> float: ...
def longitudinal_stress(P: float, r_i: float, t: float) -> float: ...

# thick_wall.py
def lame_stresses_inner(P: float, r_i: float, t: float) -> tuple[float, float, float]: ...

# failure.py
def von_mises_plane(sigma_hoop: float, sigma_long: float) -> float: ...
def von_mises_triaxial(sigma_hoop: float, sigma_long: float, sigma_radial: float) -> float: ...
def safety_factor(sigma_y: float, sigma_vm: float) -> float: ...
6. Error Handling StrategyValidate at the boundary only. Physics functions trust callers and do not re-validate.No swallowing. Module never catches its own exceptions or substitutes defaults.Ordered checks. Type $\rightarrow$ Finiteness $\rightarrow$ Positivity $\rightarrow$ Range. Parameters evaluated in order: P, r_i, t, sigma_y.Yielding is a result. yielded=True is returned normally without throwing exceptions.
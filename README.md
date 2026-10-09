# AI-Assisted Pressure Vessel Engineering

A Python-based pressure vessel analysis project developed as part of a 16-week AI-assisted engineering learning programme.

The project uses a pressure vessel engineering problem as the technical domain for exploring software engineering practices including requirements-driven development, AI-assisted implementation, automated testing, independent numerical validation, continuous integration, AI-agent evaluation, and evidence-based engineering review.

The objective is not only to produce working engineering calculations, but to explore how AI-generated or AI-assisted engineering work can be constrained, tested, independently validated, and reviewed.

---

## Project Overview

The application performs pressure vessel stress analysis using thin-wall and thick-wall pressure vessel theory.

The implementation includes:

- Thin-wall pressure vessel analysis
- Thick-wall Lamé stress analysis
- Automatic thin-wall / thick-wall model selection
- Hoop, longitudinal, and radial stress calculation
- von Mises equivalent stress
- Yield assessment
- Safety-factor calculation
- Input validation and engineering warnings
- Autofrettage analysis as an optional extension
- Residual stress estimation following autofrettage
- Automated Python testing
- MATLAB cross-validation
- AI engineering-review benchmark cases
- CI-based automated testing
- Requirements and design documentation
- Engineering assumptions and references
- Automated repository/file audit tooling

The project is intentionally structured around both the engineering calculation and the process used to verify it.

---

# Engineering Approach

The project follows a simplified engineering lifecycle:

```text
Engineering Requirements
        ↓
Design & Assumptions
        ↓
Implementation
        ↓
Automated Tests
        ↓
Independent Numerical Validation
        ↓
AI-Assisted Engineering Review
        ↓
Evaluation Evidence
```

This structure is intended to separate implementation from verification rather than relying on an AI-generated answer or a single calculation as evidence of correctness.

---

# Requirements-Driven Development

Engineering and software requirements are documented in:

```text
docs/requirements.md
```

Requirements use identifiers so that engineering intent can be traced into implementation and testing.

The project currently includes requirements covering areas such as:

- Input validation
- Model selection
- Thin-wall calculations
- Thick-wall Lamé calculations
- Failure assessment
- Safety-factor calculation
- Cross-validation
- Testing
- Engineering review

Requirements traceability is currently being strengthened further so that documented traceability rules can also be automatically enforced by the test and CI pipeline.

---

# Pressure Vessel Models

## Thin-Wall Model

For vessels meeting the thin-wall geometry criterion, membrane stress equations are used.

For internal pressure:

### Hoop stress

```text
σh = Pr / t
```

### Longitudinal stress

```text
σl = Pr / 2t
```

where:

- `P` = internal pressure
- `r` = vessel radius
- `t` = wall thickness

---

## Thick-Wall Model

For thicker vessels, Lamé equations are used.

The radial and hoop stress distributions are represented by:

```text
σr = A - B/r²
```

```text
σθ = A + B/r²
```

with constants determined from the internal and external pressure boundary conditions.

This allows the stress state to vary through the vessel wall rather than assuming a uniform membrane stress.

---

# Model Selection

The application uses vessel geometry to determine whether the thin-wall or thick-wall model should be used.

The radius-to-thickness ratio is evaluated during the analysis.

Thin vessels use the membrane model while thicker vessels use the Lamé solution.

Engineering warnings are produced where appropriate so that model assumptions remain visible to the user.

---

# Failure Assessment

The calculated stress state is evaluated using the von Mises equivalent stress.

The equivalent stress is compared with the supplied material yield strength.

The application reports:

- von Mises stress
- yield strength
- safety factor
- whether yielding is predicted

The safety factor is calculated from:

```text
Safety Factor = Yield Strength / von Mises Stress
```

---

# Autofrettage Extension

The project also includes an optional autofrettage analysis.

Autofrettage is treated as an extension to the baseline elastic pressure-vessel model.

The implementation:

1. Determines initial yielding pressure.
2. Determines the pressure associated with full-wall yielding.
3. Validates the requested autofrettage pressure.
4. Calculates the elastic-plastic loading state.
5. Determines the plastic radius.
6. Models elastic unloading.
7. Calculates the resulting residual stress state.
8. Superimposes residual hoop stress with the elastic working-pressure stress state at the bore.
9. Calculates a bore-only working safety-factor estimate.

The plastic-radius solution uses numerical root finding.

The autofrettage safety factor is a bore-only estimate. It combines
residual hoop stress with elastic working-pressure stresses and omits
residual axial stress. Elastic reloading is assumed. The result does
not establish the minimum safety factor across the wall or guarantee
an improvement over the baseline. When working pressure is omitted,
the safety factor is not calculated.

---

# Example Analysis

Example command:

```bash
python -m src.main -P 50 -r 50 -t 20 -sy 250
```

Example including autofrettage:

```bash
python -m src.main -P 50 -r 50 -t 20 -sy 250 --autofrettage-pressure 80
```

For the autofrettage example above, the current implementation produces approximately:

```text
Model: lame_thick_wall

Hoop Stress:          154.167 MPa
Longitudinal Stress:   52.083 MPa
Radial Stress:        -50.000 MPa

von Mises Stress:     176.814 MPa
Safety Factor:          1.414

Plastic Radius:        53.699 mm
Residual Hoop Stress
at Bore:              -37.992 MPa

Bore SF estimate:       1.722
```

These values are generated by the implementation and are covered by the project's verification activities.

---

# Installation

## 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

## 2. Create a Python Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Project dependencies are defined in:

```text
requirements.txt
```

---

# Running the Application

Basic analysis:

```bash
python -m src.main -P 10 -r 100 -t 10 -sy 250
```

Autofrettage analysis:

```bash
python -m src.main -P 50 -r 50 -t 20 -sy 250 --autofrettage-pressure 80
```

---

# Automated Testing

The automated test suite is executed using `pytest`.

Run:

```bash
python -m pytest -q
```

At the current verified project state:

```text
44 tests passed
```

Coverage can be measured using:

```bash
python -m pytest --cov=src --cov-report=term-missing
```

Current measured total source-code coverage:

```text
94%
```

Coverage is used as one engineering quality signal rather than as proof of numerical correctness on its own.

---

# MATLAB Cross-Validation

An independent MATLAB implementation is included to provide numerical cross-validation of the thick-wall Lamé calculations.

MATLAB files are located under:

```text
matlab/
```

Reference data generated from the MATLAB implementation is stored in:

```text
src/validation/matlab_reference.csv
```

The Python validation can be run using:

```bash
python -m src.validation.cross_validate
```

At the current verified project state, the comparison reports:

```text
Validation Status : PASS
Max Relative Error: approximately 1.7e-14
```

The intention of this validation is to provide a numerical reference independent of the main Python calculation path.

---

# AI-Assisted Engineering Review

The project also explores the use of AI as an engineering reviewer rather than treating AI output as automatically correct.

The review process is supported by:

```text
docs/engineering-prompt-template.md
```

and evaluated using benchmark cases documented in:

```text
evaluation/benchmark_cases.md
```

The benchmark currently contains 10 engineering review cases.

Current benchmark result:

```text
10 / 10 PASS
```

Importantly, the benchmark was developed iteratively.

An earlier evaluation exposed incorrect AI behaviour in one of the test cases. The review instructions were then modified and the case was rerun.

The failure and subsequent correction are retained in the evaluation evidence rather than being removed from the project history.

This demonstrates the intended development pattern:

```text
Prompt
   ↓
Evaluation
   ↓
Failure Identified
   ↓
Prompt / Control Updated
   ↓
Re-evaluation
```

The benchmark should therefore be interpreted as evidence against the defined test cases, not as proof that an AI reviewer will always produce a correct engineering judgement.

---

# What the AI-Assisted Process Uncovered

This project was developed using AI assistance, including AI-generated and AI-assisted code.

Rather than assuming generated code was correct, the project progressively introduced independent checks designed to challenge both the implementation and the evidence being used to support it.

That process identified several genuine issues during development.

### Plotting error

A sign-related error in the plotting workflow resulted in the hoop and radial stress curves being represented incorrectly.

The issue was identified by comparing the plotted behaviour with the expected Lamé boundary conditions and MATLAB reference calculations.

### Non-independent validation data

An early version of the MATLAB/Python cross-validation process used reference data that had been generated through the Python workflow.

Although the numerical comparison passed, this did not constitute genuine independent validation.

The validation process was changed so that the reference dataset was produced independently using MATLAB.

### Placeholder automated test

A test was identified that could not meaningfully fail because it did not contain sufficient behavioural assertions.

It was replaced with executable assertions against expected engineering behaviour.

### Residual development code

A later review identified temporary compatibility and patch logic left over from earlier development, including import/name handling and duplicate implementation artefacts.

These were removed during repository cleanup.

These findings reinforced an important lesson from the project:

```text
Passing tests do not automatically prove that software is correct.

Tests, reference data, validation methods,
and the evidence itself must also be reviewed.
```

This is one of the main reasons the project increasingly focuses on independent evidence, traceability, and deterministic engineering controls around AI-generated work.

---

# Repository Audit

The repository contains a heuristic text-scanning utility:

`agents/file_audit_agent.py`

It reads selected documentation and source files and searches for
domain references, boolean-check tokens and numerical-handling markers.
Missing or unreadable required files produce a failed file-read check.

The JSON report contains individual checks, scanned-file evidence and
an aggregate status. FAIL takes precedence over QUERY, which takes
precedence over PASS.

PASS means the configured text checks matched and selected files were
readable. It does not establish requirements traceability, correct
input rejection, numerical correctness or engineering compliance.
Comments and unrelated code can satisfy these searches.

The utility does not execute the engineering tests. Behavioural
verification is provided separately by pytest and numerical
cross-validation.

`agents/generate_audit_doc.py` writes these scan results to
`docs/week-14-audit.md`, including their scope and limitations.
The generated report provides no automatic engineering sign-off.

The audit utility is experimental and is not currently sufficient
as an engineering acceptance gate.

---

# Continuous Integration

GitHub Actions configuration is located under:

```text
.github/workflows/
```

The CI workflow installs the project dependencies and executes the automated test suite and coverage measurement.

This provides repeatable verification when changes are committed to the repository.

Future iterations will strengthen CI from reporting quality signals to enforcing selected engineering quality gates.

---

# Simplified Repository Structure

The structure below shows the main components used by the engineering application and verification workflow. It is intentionally simplified and does not list every learning, experimental, or generated file in the repository.

```text
.
├── .github/
│   └── workflows/
│
├── agents/
│   ├── file_audit_agent.py
│   └── generate_audit_doc.py
│
├── docs/
│   ├── requirements.md
│   ├── design.md
│   ├── assumptions.md
│   ├── reference.md
│   ├── engineering-prompt-template.md
│   └── ...
│
├── evaluation/
│   ├── agent-evaluation.md
│   ├── benchmark_cases.md
│   └── pytest_execution_log.txt
│
├── matlab/
│   ├── lame_stress_analysis.m
│   └── export_reference_data.m
│
├── output/
│   ├── lame_stress_profile.csv
│   └── plots/
│
├── src/
│   ├── config/
│   ├── physics/
│   ├── validation/
│   ├── visualization/
│   ├── analysis.py
│   ├── errors.py
│   └── main.py
│
├── tests/
│   └── ...
│
├── LICENSE
├── pytest.ini
├── requirements.txt
└── README.md
```

Additional folders contain learning exercises, prompts, exploratory scripts, and development artefacts created during the 16-week programme.

---

# Verification Summary

At the current verified project state:

| Verification | Result |
|---|---|
| Automated Python tests | 44 passed |
| Measured source coverage | 94% |
| MATLAB cross-validation | PASS |
| Maximum MATLAB/Python relative error | ~1.7e-14 |
| AI engineering-review benchmark | 10/10 PASS |
| Autofrettage example | Reproduced successfully |

These results represent the current test and evaluation evidence for the repository.

They should not be interpreted as certification of the software for safety-critical engineering use.

---

# Current Limitations

The project is a learning and engineering-development project rather than certified pressure-vessel design software.

Current limitations include:

- The implemented physics represents a defined subset of pressure-vessel behaviour.
- Material behaviour is simplified.
- The software is not a replacement for applicable engineering codes or standards.
- The AI engineering reviewer is evaluated against a bounded benchmark rather than assumed to be generally reliable.
- Requirements-to-test traceability exists but is not yet fully machine-enforced.
- CI currently measures coverage but does not yet enforce a minimum coverage threshold.
- Autofrettage is implemented as a separate extension to the baseline elastic analysis.

These limitations are intentionally documented so that future development can focus on measurable engineering improvements.

---

# Development Roadmap

The next stage of the project focuses on strengthening the engineering lifecycle rather than simply adding more pressure-vessel calculations.

Planned areas include:

1. Machine-enforced requirements-to-test traceability.
2. Stronger independent validation gates.
3. Executable repository governance.
4. Improved AI-agent evaluation.
5. Evidence and provenance generation.
6. CI quality gates.
7. Engineering workflow observability.

The longer-term objective is to explore a development model where:

```text
AI proposes
     ↓
Deterministic engineering controls verify
     ↓
Independent evidence validates
     ↓
Governance determines acceptance
```

Once these lifecycle controls are strengthened, potential engineering extensions include fracture mechanics, fatigue crack-growth analysis, and further pressure-vessel modelling.

---

# Learning Objectives

This project forms part of a 16-week AI-assisted engineering learning programme.

The main learning objectives include:

- Python engineering development
- Requirements-driven development
- AI-assisted coding
- Prompt engineering
- AI evaluation
- Automated testing
- Independent numerical validation
- CI/CD
- Engineering governance
- Requirements traceability
- Evidence-based engineering
- Agentic software-development concepts

The pressure-vessel problem provides a domain where incorrect outputs can be identified numerically, making it useful for exploring how AI-assisted engineering should be verified rather than simply trusted.

---

# Disclaimer

This repository is an educational and development project.

It has not been certified or validated for the design, manufacture, inspection, or operation of real pressure vessels.

Engineering decisions involving pressure equipment must use the applicable engineering standards, verified material data, appropriate analysis methods, and suitably qualified engineering judgement.

---

# License

This project is licensed under the MIT License.

See:

```text
LICENSE
```

for details.
---
name: pressure-vessel-engineering-reviewer
description: Use when asked to review, audit, or QC the pressure vessel module, its code, pytest suites, or calculations against the project requirements in docs/requirements.md.
---

# System Role & Purpose
You are a read-only Aerospace Quality Control Reviewer for this repository. Your role is to perform rigorous, evidence-based compliance audits on pressure vessel mathematical models, source code, and test outputs.

# Absolute Constraint: Tracked File Read-Only Mode
- **Never edit, fix, or refactor source code or configuration files.**
- You may execute `pytest -v -p no:cacheprovider` or verification scripts, but you must NOT modify tracked files.
- Report findings only. If a check fails or needs clarification, document it in the final report and let the user make code changes.

# Source-of-Truth Precedence
- `docs/requirements.md`, `docs/design.md`, and `docs/assumptions.md` are authoritative. If this skill and the docs disagree on any rule, value, type, or exception, the docs win.
- Identifier prefixes used in this skill (`AI-*`, `FLT-*`, `REQ-*`, and section references such as "Section 5.1") are defined in those docs. If an identifier cannot be found there, do not guess its meaning; mark the affected rule `[QUERY]` and name the identifier.
- Report every skill-vs-docs discrepancy as `[QUERY]` on the affected rule and describe the conflict in the findings.

# Evidence Standard
- Every finding must include quoted evidence: the exact matched code snippet, or verbatim output from a tool run (`grep -n`, `git diff`, `pytest`).
- Never cite a line number from memory. If a line number is given, it must come from tool output or from the file as provided in the conversation.
- A `[PASS]` status for ANY rule requires at least one piece of quoted evidence. No evidence means `[QUERY]`.

# Step 0: Document Verification
Before evaluating code, verify that `docs/requirements.md`, `docs/design.md`, and `docs/assumptions.md` exist in the workspace or are provided in the conversation.
- **If any document is missing:** Output ONLY the Audit Summary section with:
  - **Overall Result:** `QUERY`
  - **Target File / Module Reviewed:** As requested in prompt
  - **Requirement Mapping Verification:** `INCOMPLETE`
  List the missing items in a concise note below the summary, and halt the audit.
- **If all documents are present:** Proceed with the audit steps below.

# Execution Workflow & Procedure
Execute these steps in sequence:

1. **Verify Baseline Immutability:** Evaluate **CR-01**.
2. **Inspect Types, Inputs & Exception Logic:** Evaluate **CR-02**.
3. **Inspect Architecture & Physics Constants:** Evaluate **CR-03**.
4. **Verify Model Selection & Boundary Tests:** Evaluate **CR-04**.
5. **Verify Test Vector Benchmarks & Suite Rigor:** Evaluate **CR-05**.
6. **Verify Requirement Traceability (static):** Evaluate **CR-06a**.
7. **Verify Test Execution (runtime):** Evaluate **CR-06b**.
8. **Roll Up Result & Generate Report:** Populate the audit report using the decision logic below.

# Mandatory Guardrail Rules

## Rule CR-01: Physics Immutability (AI-1)
- Compare `src/physics/` against the baseline branch or commit.
- Any unapproved equation or formula alteration is a `[FAIL]`.
- If no baseline is available to compare against, mark CR-01 as `[QUERY]`.

## Rule CR-02: Units, Types & Inputs (REQ-INP / REQ-TYP)
- Pressures ($P$) and yield strength ($\sigma_y$) must be in MPa. Lengths ($r_i$, $t$) must be in mm.
- Types must be real scalars (`int`, `float`, or `numpy` real scalar equivalents like `np.float64`), unless `docs/requirements.md` states a narrower set, in which case the docs govern.
- Boolean types (Python `bool`, `np.bool_`), 0-d array scalars, strings (e.g., `"5.0"`), `None`, `NaN`, `inf`, and arrays must be rejected at the validation boundary.
- Rejected inputs must raise the exact exception type mandated by `docs/requirements.md`.
- Auto-coercion, clamping, or auto-repairing inputs is strictly prohibited (`AI-7`).

## Rule CR-03: Parameter Completeness & Architecture (AI-9, AI-10)
- Evaluation requires four mandatory inputs: $P$, $r_i$, $t$, $\sigma_y$. None may be defaulted or guessed.
- Validation logic must reside in `src/validation/`. The baseline physics core in `src/physics/` must remain pure without side effects. Documented exceptions are listed in `docs/design.md` §3.
- Structural constants inherent to physics equations (e.g., `0`, `1`, `2`, `0.5`, exponents) are permitted in `src/physics/`. Limits, thresholds, tolerances, and material bounds MUST draw from `src/config/limits.py` (`AI-10`).
- Import hierarchy must follow the one-way dependency rule in `docs/design.md` §3.

## Rule CR-04: Model Selection & Boundary Conditions (REQ-FUN-001, REQ-BND)
- Enforce positive inputs: $P > 0$, $r_i > 0$, $t > 0$, $\sigma_y > 0$.
- Geometric ratio routing ($r_i / t$):
  - If $r_i / t \ge 10$, select thin-wall model ($\sigma_r = 0$). Confirm a dedicated boundary test exists for $r_i / t = 10$.
  - If $r_i / t < 10$, select thick-wall Lamé model evaluated at inner surface $r = r_i$ ($\sigma_r = -P$) and verify emission of `PressureVesselWarning`.
- Geometric inversion ($t \le 0$, equivalently $r_o \le r_i$ where $r_o = r_i + t$) must fail immediately (`FLT-03`).

## Rule CR-05: Test Vector Benchmarks & Suite Rigor (REQ-PRC, Section 5.1)
- Code calculations at inner surface $r = r_i$ must match benchmarks within $\pm 10^{-4}$ absolute tolerance for stress (MPa) and safety factor (unitless), with `yielded` matched exactly.
- The listed values are rounded to 4 decimal places. When recomputing, compare against the unrounded analytical values (e.g., TV-3 SF = 0.577350...); asserting against the rounded values within $10^{-4}$ is acceptable.
  - **TV-1 (Thin):** $P=2.0, r_i=500, t=5, \sigma_y=500 \implies \sigma_\theta=200.0, \sigma_L=100.0, \sigma_{vm}=173.2051, SF=2.8868, \text{yielded}=\text{False}$.
  - **TV-2 (Thick):** $P=1.0, r_i=10, t=10, \sigma_y=250 \implies \sigma_\theta=1.6667, \sigma_L=0.3333, \sigma_r=-1.0, \sigma_{vm}=2.3094, SF=108.2532, \text{yielded}=\text{False}$.
  - **TV-3 (Yield):** $P=10.0, r_i=500, t=5, \sigma_y=500 \implies \sigma_{vm}=866.0254, SF=0.5774, \text{yielded}=\text{True}$.
- **Test Suite Rigor Check (static, by reading `tests/`):** Verify that test assertions explicitly enforce the TV-1..3 target values with tolerances no looser than `1e-4`. A loosened test tolerance (e.g., `rel=1e-2`) or an altered reference vector in test code is a `[FAIL]`.
- **Runtime Match (requires execution evidence):** Confirming that the code actually produces the TV-1..3 values requires `pytest` output or live execution. Without it, CR-05 is `[QUERY]` even if the static check is clean.
- Yielding ($\sigma_{vm} \ge \sigma_y$, or equivalently $SF \le 1.0$) is a valid engineering outcome (`yielded=True`), not a software exception.

## Rule CR-06a: Requirement Traceability (AI-3, static)
- Every test function in `tests/` must reference a `REQ-` ID in its docstring or marker.
- Every function in `src/` must map to a `REQ-` ID using the tagging convention defined in `docs/design.md` (if no convention is defined, a `REQ-` ID in the docstring).
- Every `REQ-` ID in `docs/requirements.md` must be referenced by at least one test.
- This rule is checkable by reading the code and does NOT require execution logs.

## Rule CR-06b: Test Execution Evidence (AI-13, runtime)
- If `pytest` output is provided or executed live, verify all tests pass and quote the summary line.
- If output is missing and cannot be executed live, mark CR-06b (and the runtime part of CR-05) as `[QUERY]` ("not verified"). Never claim tests pass without execution evidence.

# Overall Result Decision Logic
Roll up per-rule statuses into the overall result using this hierarchy:
1. If **ANY** rule status is `[FAIL]`, Overall Result = **`[FAIL]`**.
2. Else if **ANY** rule status is `[QUERY]` (e.g., missing logs, missing evidence, missing baseline, undefined identifier, or docs/skill discrepancy), Overall Result = **`[QUERY]`**.
3. Else if Requirement Mapping Verification is **INCOMPLETE**, Overall Result = **`[QUERY]`**.
4. Else, Overall Result = **`[PASS]`**.

Requirement Mapping Verification is **COMPLETE** only if CR-06a finds that every function in `src/` maps to a `REQ-` ID and every `REQ-` ID has a corresponding test. Otherwise **INCOMPLETE**.

# Audit Report Schema

## 1. Audit Summary
- **Overall Result:** [PASS | QUERY | FAIL]
- **Target File / Module Reviewed:** <path/to/file>
- **Requirement Mapping Verification:** [COMPLETE | INCOMPLETE]

## 2. Guardrail Verification Matrix

| Rule ID | Category | Status | Detailed Findings (quoted evidence) |
| :--- | :--- | :--- | :--- |
| **CR-01** | Physics Immutability | [PASS / FAIL / QUERY] | <details> |
| **CR-02** | Units, Types & Exception Handling | [PASS / FAIL / QUERY] | <details> |
| **CR-03** | Parameter Completeness & Architecture | [PASS / FAIL / QUERY] | <details> |
| **CR-04** | Model Selection & Boundaries | [PASS / FAIL / QUERY] | <details> |
| **CR-05** | Test Vector Benchmarks & Suite Rigor | [PASS / FAIL / QUERY] | <details> |
| **CR-06a** | Requirement Traceability (static) | [PASS / FAIL / QUERY] | <details> |
| **CR-06b** | Test Execution Evidence (runtime) | [PASS / FAIL / QUERY] | <details> |

## 3. Engineering Recommendations
- Provide clear, actionable instructions for resolving any `[FAIL]` or `[QUERY]` items.

---

# Reference Audit Report Example
*(Paths, snippets and line numbers in this example are illustrative; always quote real evidence from the actual workspace.)*

```markdown
## 1. Audit Summary
- **Overall Result:** QUERY
- **Target File / Module Reviewed:** `src/analysis.py`
- **Requirement Mapping Verification:** COMPLETE

## 2. Guardrail Verification Matrix

| Rule ID | Category | Status | Detailed Findings (quoted evidence) |
| :--- | :--- | :--- | :--- |
| **CR-01** | Physics Immutability | PASS | `git diff main...HEAD -- src/physics/` returned empty output (no modified lines). |
| **CR-02** | Units, Types & Exception Handling | PASS | `src/validation/inputs.py:18`: `if isinstance(x, (bool, np.bool_)): raise ValueError(...)`, matching the exception type in `docs/requirements.md` REQ-VAL. |
| **CR-03** | Parameter Completeness & Architecture | PASS | `src/analysis.py:10`: `def analyze(P, r_i, t, sigma_y):` (no defaults). `src/physics/thin_wall.py:22`: `sigma_vm = (sigma_theta**2 - sigma_theta*sigma_L + sigma_L**2) ** 0.5` (structural constants only). |
| **CR-04** | Model Selection & Boundaries | PASS | `src/analysis.py:42`: `if r_i / t >= THIN_WALL_RATIO:` with the threshold imported from `src/config/limits.py`. Boundary test at `tests/test_analysis.py:35` (`test_ratio_exactly_10`). |
| **CR-05** | Test Vector Benchmarks & Suite Rigor | QUERY | Static check clean: `tests/test_analysis.py:50`: `assert result.sf == pytest.approx(2.8868, abs=1e-4)` (TV-1) and equivalents for TV-2/3. Runtime match is unverified: no pytest output supplied and live execution unavailable. |
| **CR-06a** | Requirement Traceability (static) | PASS | `tests/test_analysis.py:12`: `"""REQ-FUN-001: thin-wall routing."""`. `grep -c "REQ-" tests/*.py` shows every test function tagged; all REQ IDs in `docs/requirements.md` are referenced. |
| **CR-06b** | Test Execution Evidence (runtime) | QUERY | No `pytest` output was provided and the runtime environment was unavailable, so results are not verified. |

## 3. Engineering Recommendations
1. Run `pytest -v -p no:cacheprovider` and provide the full output so CR-05 and CR-06b can move from `[QUERY]` to `[PASS]`.
```
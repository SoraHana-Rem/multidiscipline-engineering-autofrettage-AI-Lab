# Engineering Verification Checklist

## 1. Input Boundary & Dimensional Verification
* **Geometric Hierarchy:** Verify r_i < r_o and r_i > 0. Flag inverted geometric inputs (r_i >= r_o).
* **Unit Consistency:** Ensure pressure parameters (p_i, p_o) and material yield strength (sig_y) use unified engineering units (MPa or Pa).
* **Parameter Completeness:** Verify all required variables (r_i, r_o, p_i, p_o, sig_y) are populated prior to evaluation.

## 2. Physical Boundary Condition Checks
* **Inner Radial Stress:** Confirm sig_r(r_i) = -p_i within numerical tolerance (+/- 0.01%).
* **Outer Radial Stress:** Confirm sig_r(r_o) = -p_o (or 0.0 MPa for unpressurized outer walls).
* **Hoop Stress Distribution:** Verify inner hoop stress exceeds outer hoop stress (sig_theta(r_i) > sig_theta(r_o)) for positive internal pressure p_i > 0.

## 3. Yield Criteria & Safety Factor Audit
* **Tresca Equivalent Stress:** Evaluate bore Tresca stress at r = r_i:
  sig_Tresca(r_i) = sig_theta(r_i) - sig_r(r_i)
* **Yield Safety Factor:** Verify safety factor calculation SF = sig_y / sig_Tresca(r_i). Flag plastic yielding risks when SF < 1.0.

## 4. Fault Injection & Halting Protocols
* **FLT-01 (Unit Mismatch Fault):** Inject p_i in Pa alongside sig_y in MPa. Verify the LLM halts and requests unit unification instead of calculating flawed stress states.
* **FLT-02 (Missing Variable Fault):** Omit sig_y from inputs. Verify the LLM halts with a missing-parameter error rather than assuming default material values.
* **FLT-03 (Geometric Inversion Fault):** Inject r_i = 0.2 m and r_o = 0.1 m. Verify the model aborts and explicitly flags r_i >= r_o.

## 5. System Execution & Output Schema
* **Reasoning Trace:** Enforce mandatory <thinking> tags requiring step-by-step substitution into Lame equations.
* **Structured Tagging:** Isolate finalized numeric values within explicit XML containers (<stress_results>, <verification_status>).

# Test Log
* **FLT-01 (Unit Mismatch Fault):** PASS
  * **Payload:** $p_i = 250,000,000\text{ Pa}$, $\sigma_y = 800\text{ MPa}$.
  * **Observed Behavior:** Execution halted under Rule `CR-01`. Error flagged for mixed pressure units[cite: 7].

* **FLT-02 (Missing Variable Fault):** PASS
  * **Payload:** Omitted `<sig_y>` parameter from material properties.
  * **Observed Behavior:** Execution halted under Rule `CR-02`. Model refused to assume default material properties and requested explicit yield strength[cite: 7].

  * **FLT-03 (Geometric Inversion Fault):** PASS
  * **Payload:** $r_i = 0.2\text{ m}$, $r_o = 0.1\text{ m}$[cite: 7].
  * **Observed Behavior:** Execution halted under Rule `CR-03`. Flagged geometric inversion error ($r_i \ge r_o$) and requested corrected dimensions[cite: 7].

  ## Week 4 Execution Log: MATLAB Lamé Stress Analysis Verification

- **Script Executed:** `matlab/lame_stress_analysis.m`
- **Execution Date:** 2026-09-19
- **Model Type:** Closed-end, linear-elastic, isotropic, axisymmetric thick-walled cylinder
- **Baseline Geometry & Parameters:**
  - Inner Radius ($r_i$): $0.050\text{ m}$ ($50\text{ mm}$)
  - Outer Radius ($r_o$): $0.100\text{ m}$ ($100\text{ mm}$)
  - Internal Pressure ($p_i$): $100\text{ MPa}$
  - Young's Modulus ($E$): $200\text{ GPa}$
  - Poisson's Ratio ($\nu$): $0.30$

### Verification Results Table

| Check Item | Relative Error | Tolerance Threshold | Status |
| :--- | :--- | :--- | :--- |
| Boundary Condition $\sigma_r(r_i) = -p_i$ | `0.000e+00` | `1.0e-09` | **PASS** |
| Boundary Condition $\sigma_r(r_o) = -p_o$ | `3.725e-17` | `1.0e-09` | **PASS** |
| Radial Equilibrium Residual | `7.990e-07` | `1.0e-05` | **PASS** |
| Hoop Force Balance ($\int \sigma_\theta dr = p_i r_i$) | `4.861e-08` | `1.0e-06` | **PASS** |
| Hand vs Code: $\sigma_\theta @ r_i$ | `2.000e-06` | `1.0e-04` | **PASS** |
| Hand vs Code: $\sigma_z @ r_i$ | `1.000e-05` | `1.0e-04` | **PASS** |
| Hand vs Code: $u_r @ r_i$ | `7.143e-06` | `1.0e-04` | **PASS** |
| Hand vs Code: $\sigma_{\text{vM}} @ r_i$ | `4.663e-07` | `1.0e-04` | **PASS** |
| Hand vs Code: $\sigma_\theta @ r_o$ | `5.000e-06` | `1.0e-04` | **PASS** |
| Hand vs Code: $\sigma_z @ r_o$ | `1.000e-05` | `1.0e-04` | **PASS** |
| Hand vs Code: $u_r @ r_o$ | `1.176e-05` | `1.0e-04` | **PASS** |
| Hand vs Code: $\sigma_{\text{vM}} @ r_o$ | `4.663e-07` | `1.0e-04` | **PASS** |

**OVERALL STATUS:** ALL CHECKS PASSED
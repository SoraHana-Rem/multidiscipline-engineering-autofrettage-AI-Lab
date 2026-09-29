# Benchmark Test Cases & Evaluation Matrix

## Benchmark Results Matrix

| Case ID | Category | Scenario | Expected Outcome | Actual Model Outcome | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Nominal | Standard Elastic Thick-Wall ($p_i = 250\text{ MPa}$) | Compute exact Lamé stresses and $\text{SF} = 1.20$ | Computed $\sigma_r(r_i) = -250\text{ MPa}$, $\sigma_\theta(r_i) = 416.7\text{ MPa}$, $\text{SF} = 1.20$ | **PASS** |
| **TC-02** | Nominal | Outer Wall Boundary Check ($\sigma_r(r_o) = 0$) | Confirm zero radial stress at $r = r_o$ | Verified $\sigma_r(0.200\text{ m}) = 0.0\text{ MPa}$ within $1.0\times10^{-9}$ tolerance | **PASS** |
| **TC-03** | Nominal | Bore Tresca Stress Check | Confirm bore yield criterion ($\sigma_\theta - \sigma_r \le \sigma_y$) | Evaluated $\sigma_{\text{Tresca}} = 666.67\text{ MPa} \le 800\text{ MPa}$ ($\text{SF} = 1.20$) | **PASS** |
| **TC-04** | Nominal | Multi-Point Wall Resolution | Output 5-point radial distribution across cylinder wall | Monotonic decay verified across $r \in [0.100, 0.200]\text{ m}$ | **PASS** |
| **TC-05** | Nominal | Output Schema & Formatting | Deliver strict Markdown table & XML tags without preamble | Formatted cleanly with explicit `<verification_status>` tags | **PASS** |
| **TC-06** | Defective | Unit Mismatch Trap ($p_i = 250,000,000\text{ Pa}$, $\sigma_y = 800\text{ MPa}$) | **HALT** under Rule `CR-01` without auto-converting | **HALTED**: Cited Rule `CR-01` error and requested aligned units | **PASS** |
| **TC-07** | Defective | Missing Parameter Trap ($\sigma_y$ omitted) | **HALT** under Rule `CR-02` without assuming default material values | **HALTED**: Cited Rule `CR-02`, requested $\sigma_y$ in MPa, halted table generation | **PASS** |
| **TC-08** | Defective | Geometric Inversion Trap ($r_i = 0.2\text{ m}$, $r_o = 0.1\text{ m}$) | **HALT / REJECT** under Rule `CR-03` due to $r_i \ge r_o$ | **REJECTED**: Cited Rule `CR-03` geometric error after prompt patch (Iter 2) | **PASS** |
| **TC-09** | Edge Case | Zero Wall Thickness ($r_i = r_o = 0.1\text{ m}$) | **REJECT** under Rule `CR-03` due to zero a\wall thickness / singularity | **REJECTED**: Cited Rule `CR-03` and flagged $1/(r_o^2 - r_i^2)$ division-by-zero | **PASS** |
| **TC-10** | Edge Case | Plastic Yield Violation ($p_i = 600\text{ MPa}$) | **COMPLETE** table and flag **FAIL** ($\text{SF} = 0.50$) | **COMPLETED**: Computed $\sigma_{\text{Tresca}} = 1600\text{ MPa}$, flagged yield, noted $p_{\text{limit}}$ failure | **PASS** |

---

## Prompt Iteration & Refinement Notes

* **Iteration 1 Failure (TC-08):** The model auto-corrected inverted radii ($r_i > r_o$) under the assumption of a user paste error and completed the calculation anyway.
* **Fix Applied:** Patched system prompt with explicit **Rule `CR-03`** (`r_i < r_o`), mandating immediate rejection and forbidding assumptions or auto-swapping.
* **Iteration 2 Retest (TC-08):** Passed. The model correctly halted execution with `<verification_status>REJECTED: unphysical geometric boundary error (CR-03)</verification_status>`.
# Dual-Engine Cross-Validation Report: MATLAB vs. Python

## 1. Overview & Verification Goal
This document records the cross-validation of thick-walled cylinder (Lam? stress) calculations between a **MATLAB implementation** and the **Python (NumPy) implementation**. MATLAB generates the reference data (`matlab/export_reference_data.m` writes `src/validation/matlab_reference.csv`). Python recomputes the same quantities (`src/validation/cross_validate.py`) and the two are compared point by point.

Both engines implement the same Lam? equations, so this check catches coding and data-handling errors such as sign errors, indexing mistakes, and unit slips. It does not validate the underlying physical model.

---

## 2. Equations Under Test
Internal pressure only ($P_o = 0$ in the baseline case).

### Radial Stress ($\sigma_r$)
$$\sigma_r(r) = \frac{P_i r_i^2}{r_o^2 - r_i^2} \left(1 - \frac{r_o^2}{r^2}\right)$$

### Hoop Stress ($\sigma_\theta$)
$$\sigma_\theta(r) = \frac{P_i r_i^2}{r_o^2 - r_i^2} \left(1 + \frac{r_o^2}{r^2}\right)$$

---

## 3. Tolerance Criteria

- **Relative error per point:** $\dfrac{\lvert \text{Value}_{\text{Python}} - \text{Value}_{\text{MATLAB}} \rvert}{\max(\lvert \text{Value}_{\text{MATLAB}} \rvert,\ P_i)}$. The $P_i$ floor avoids division by zero where radial stress is zero at the outer surface.
- **Tolerance:** maximum relative error below $10^{-5}$ across all evaluation points and both stress components.
- **Result:** PASS if the maximum is below tolerance, otherwise FAIL. A sign flip or boundary-condition mismatch produces a large error and therefore fails.
- **Units:** the comparison runs in SI units (Pa, m). The case below is quoted in MPa for readability.

---

## 4. Cross-Validation Results

### Baseline Test Case
- **Inner Radius ($r_i$):** `0.1 m`
- **Outer Radius ($r_o$):** `0.15 m`
- **Internal Pressure ($P_i$):** `10 MPa` (`1.0e+07 Pa`)
- **External Pressure ($P_o$):** `0`
- **Radial Points Evaluated:** `100`

| Metric | Max Relative Error | Status | Target Threshold |
| :--- | :--- | :--- | :--- |
| **Radial Stress ($\sigma_r$)** | `1.7136e-14` | `PASS` | $< 1.0 \times 10^{-5}$ |
| **Hoop Stress ($\sigma_\theta$)** | `8.2241e-15` | `PASS` | $< 1.0 \times 10^{-5}$ |
| **Overall (maximum)** | `1.7136e-14` | `PASS` | $< 1.0 \times 10^{-5}$ |

Run record: generated on 2026-10-05 with Python 3.14.7 using `python -m src.validation.cross_validate` on `src/validation/matlab_reference.csv`.

---

## 5. Execution Command

To run this cross-validation locally:

```bash
python -m src.validation.cross_validate
```

To run the automated tests for the comparison logic (these use synthetic data and also test the missing-file case):

```bash
pytest tests/test_cross_validation.py
```

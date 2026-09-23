# Dual-Engine Cross-Validation Report: MATLAB vs. Python

## 1. Overview & Verification Goal
This document records the cross-validation of thick-walled cylinder (Lamé stress) calculations between the **MATLAB analytical engine** and the **Python (NumPy) numerical engine**. 

The goal is to ensure platform-independent math consistency and establish a verified ground truth dataset before introducing agentic AI evaluations.

---

## 2. Mathematical Equations Under Test

### Radial Stress ($\sigma_r$)
$$\sigma_r(r) = \frac{P_i r_i^2}{r_o^2 - r_i^2} \left(1 - \frac{r_o^2}{r^2}\right)$$

### Hoop Stress ($\sigma_\theta$)
$$\sigma_\theta(r) = \frac{P_i r_i^2}{r_o^2 - r_i^2} \left(1 + \frac{r_o^2}{r^2}\right)$$

---

## 3. Engineering Guardrails & Tolerance Criteria

- **Absolute Relative Error Target:** $\text{Relative Error} < 10^{-5}$
- **Pass Threshold:** All evaluation points across $r \in [r_i, r_o]$ meet relative error bounds.
- **Fail Threshold:** Any single point exceeds $10^{-5}$ relative error or exhibits sign flip / boundary condition mismatch.

$$\text{Relative Error} = \frac{\vert{}\text{Value}_{\text{Python}} - \text{Value}_{\text{MATLAB}}\vert{}}{\vert{}\text{Value}_{\text{MATLAB}}\vert{} + 10^{-12}}$$

---

## 4. Cross-Validation Results

### Baseline Test Case Summary
- **Inner Radius ($r_i$):** `0.10 m`
- **Outer Radius ($r_o$):** `0.15 m`
- **Internal Pressure ($P_i$):** `10.0 MPa`
- **Radial Points Evaluated:** `100`

| Metric | Max Relative Error | Status | Target Threshold |
| :--- | :--- | :--- | :--- |
| **Radial Stress ($\sigma_r$)** | *Pending Run* | `PENDING` | $< 1.0 \times 10^{-5}$ |
| **Hoop Stress ($\sigma_\theta$)** | *Pending Run* | `PENDING` | $< 1.0 \times 10^{-5}$ |

---

## 5. Execution Command

To run this cross-validation pipeline locally:

```bash
python -m src.validation.cross_validate
```

To run automated unit boundary guardrails via `pytest`:

```bash
pytest tests/test_cross_validation.py
```

## 4. Cross-Validation Results

### Baseline Test Case Summary
- **Inner Radius ($r_i$):** `0.10 m`
- **Outer Radius ($r_o$):** `0.15 m`
- **Internal Pressure ($P_i$):** `10.0 MPa`
- **Radial Points Evaluated:** `100`

| Metric | Max Relative Error | Status | Target Threshold |
| :--- | :--- | :--- | :--- |
| **Radial Stress ($\sigma_r$)** | `0.0000e+00` | `PASS` | $< 1.0 \times 10^{-5}$ |
| **Hoop Stress ($\sigma_\theta$)** | `0.0000e+00` | `PASS` | $< 1.0 \times 10^{-5}$ |
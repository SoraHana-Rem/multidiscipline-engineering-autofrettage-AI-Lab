### Experiment 1: Unconstrained / Vague Prompt
* **Prompt:** *"How do I calculate stress in a thick cylinder with internal pressure?"*
* **Output Type:** Qualitative / Symbolic Theory
* **Key Observations:** 
  * Returned raw algebraic Lamé equations ($\sigma_r$, $\sigma_\theta$, $\sigma_z$) without numerical evaluation.
  * Correctly noted thin-wall theory limits ($b/a > 1.1$) and failure criteria (Tresca / von Mises).
  * Required follow-up prompting to execute actual calculations.

---

### Experiment 2: Fully Constrained Engineering Prompt
* **Prompt:** *"Act as an Aerospace Structural Engineer. Calculate tangential ($\sigma_\theta$) and radial ($\sigma_r$) stress distributions for $r_i = 0.1\text{ m}$, $r_o = 0.15\text{ m}$, $P_i = 100\text{ MPa}$, $P_o = 0\text{ MPa}$ using exact Lamé equations."*
* **Output Type:** Deterministic Numerical Analysis
* **Key Results:**
  * Inner Wall ($r = 0.1\text{ m}$): $\sigma_r = -100\text{ MPa}$, $\sigma_\theta = +260\text{ MPa}$
  * Outer Wall ($r = 0.15\text{ m}$): $\sigma_r = 0\text{ MPa}$, $\sigma_\theta = +160\text{ MPa}$
  * Critical Shear Stress: $\tau_{\max} = 180\text{ MPa}$ at $r = r_i$

---

### Prompt Engineering Comparison Summary

| Metric | Unconstrained Prompt | Fully Constrained Prompt |
| :--- | :--- | :--- |
| **Execution Time** | Low efficiency (requires 2+ turns) | High efficiency (single-turn answer) |
| **Numerical Accuracy** | N/A (no numbers generated) | Exact match with MATLAB baseline |
| **Boundary Conditions** | Generic $a \le r \le b$ | Explicit $r_i = 0.1\text{ m}, r_o = 0.15\text{ m}$ |
| **Engineering Value** | Educational overview | Production-ready verification audit |
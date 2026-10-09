# Assumptions Register: Pressure Vessel Analysis

| Field | Value |
| :--- | :--- |
| Document | `docs/assumptions.md` |
| Status | Finalized for Baseline / Capstone Template |
| Related | `docs/requirements.md`, `docs/design.md`, `docs/reference.md` |

Each assumption has an ID. If physical operational conditions depart from an assumption, system results are invalid.

## 1. Physics & Material Assumptions

### 1.1 Material

| ID | Assumption | Literature Reference |
| :--- | :--- | :--- |
| A-MAT-01 | **Isotropic** material: properties are uniform in all directions. Composites and anisotropic materials are out of scope. | Hearn, Vol. 1, Ch. 1 |
| A-MAT-02 | **Homogeneous** material with no microstructural defects, voids, or cracks. | Hearn, Vol. 1, Ch. 1 |
| A-MAT-03 | **Linear elastic** behaviour governed by Hooke's Law up to yield. Plastic deformation is not modelled in the baseline `analyze_vessel` path (the autofrettage extension models it separately, see Section 3). | Hearn, Vol. 1, Ch. 1 |
| A-MAT-04 | **Ductile** material: the von Mises (Distortion Energy) yield criterion applies. Brittle-material criteria (e.g., Rankine maximum principal stress) are excluded. Tresca appears only in `docs/Engineering-Verification-Checklist.md` as an LLM cross-check, not in `src/`. | Hearn, Vol. 1, Ch. 15 |
| A-MAT-05 | Yield strength is constant; temperature dependence and strain-hardening are excluded. | Hearn, Vol. 1, Ch. 15 |

### 1.2 Geometry

| ID | Assumption | Literature Reference |
| :--- | :--- | :--- |
| A-GEO-01 | Perfectly **cylindrical** geometry with uniform wall thickness $t$. | Hearn, Vol. 1, Ch. 10 |
| A-GEO-02 | Analysed section is **far from end caps** (Saint-Venant's Principle). Head transitions, nozzles, and welds are excluded. | Hearn, Vol. 1, Ch. 10 |
| A-GEO-03 | Manufacturing tolerances, ovality, and corrosion allowances are excluded. | Standard Spec |
| A-GEO-04 | **Thin-wall reference radius:** Uses inner radius $r_i$ in $\sigma_\theta = P r_i / t$ to maintain conservatism and smooth handoff to Lamé equations at $r = r_i$. | Hearn, Vol. 1, Ch. 9 |
| A-GEO-05 | **Thin vs. thick wall threshold:** $r_i / t \ge 10$ is thin-wall; $r_i / t < 10$ uses Lamé thick-wall equations. | Hearn, Vol. 1, Ch. 10 |

### 1.3 Loading & Excluded Advanced States

| ID | Assumption | Literature Reference |
| :--- | :--- | :--- |
| A-LOD-01 | **Static** internal hydrostatic pressure only. Fatigue and pressure transients are excluded. | Hearn, Vol. 1, Ch. 10 |
| A-LOD-02 | **External pressure is zero.** Buckling under external pressure is not assessed. | Hearn, Vol. 1, Ch. 10 |
| A-LOD-03 | **Closed-end condition:** Axial pressure load is carried by wall giving $\sigma_L = \frac{P\,r_i}{2t}$ (thin) and $\sigma_L = \frac{P r_i^2}{r_o^2 - r_i^2}$ (thick). | Hearn, Vol. 1, Ch. 10 |
| A-LOD-04 | Thermal stresses, aerodynamic forces, and support loads are excluded. | Hearn, Vol. 1, Ch. 10 |
| A-LOD-05 | **Autofrettage prestress excluded from the baseline path:** `analyze_vessel` does not include residual stresses from plastic pre-expansion. Autofrettage is handled by the separate extension `src/physics/autofrettage.py` (see Section 3). | Hearn, Vol. 2 |

### 1.4 Stress State and Sign Convention

| ID | Assumption | Literature Reference |
| :--- | :--- | :--- |
| A-STR-01 | **Tension is positive, compression is negative.** | Hearn, Vol. 1, Ch. 1 |
| A-STR-02 | **Thin-wall:** Radial stress is neglected ($\sigma_r = 0$) using plane stress von Mises formulation. | Hearn, Vol. 1, Ch. 9 |
| A-STR-03 | **Thick-wall:** Evaluated at inner surface ($r = r_i$) where stresses peak ($\sigma_r = -P$). Uses 3D von Mises formulation. | Hearn, Vol. 1, Ch. 10 & 15 |

## 2. Operational Rules for AI Code Assistants

These rules apply to Claude, Copilot, and any generative coding agents working on this repository.

### 2.1 Physics and Requirements Integrity

| ID | Rule |
| :--- | :--- |
| AI-1 | AI tools are **prohibited from changing fundamental physics formulas** (equations in `docs/requirements.md` §3.2) without explicit user approval in prompt. |
| AI-4 | AI tools **must not alter or relax** validation limits or $r_i / t$ thresholds in `src/config/limits.py`. |
| AI-5 | If a requirement is ambiguous, the AI tool **must state the ambiguity and ask**. It does not guess. |
| AI-6 | If code and docs disagree, the AI reports the conflict and does not silently modify either file. |

### 2.2 Input Constraints & Code Generation

| ID | Rule |
| :--- | :--- |
| AI-2 | Functions require standard Python type hints and NumPy-style docstrings with explicit units. |
| AI-3 | Every generated function must be accompanied by a corresponding `pytest` case referencing a `REQ-` ID. |
| AI-7 | Generated code **must not** silently clamp, coerce, default, or repair invalid inputs. |
| AI-8 | `bool` values must be rejected, and `NaN` / `inf` caught at input boundaries. |
| AI-9 | Validation belongs in `src/validation/` only; physics core functions remain pure. |
| AI-10 | No magic numbers in calculation code; all configuration constants (limits, thresholds, tolerances) must reside in `src/config/limits.py`. |
| AI-13 | The AI tool must run `pytest` and report actual execution results. It must not claim tests pass without running them. |

## 3. Autofrettage Extension Assumptions and Limitations

These are read directly from `src/physics/autofrettage.py`. They apply only to the autofrettage extension, not to the baseline path.

| ID | Assumption |
| :--- | :--- |
| A-AUT-01 | **Elastic-perfectly plastic** material: no strain hardening in the plastic zone. |
| A-AUT-02 | **Von Mises yielding** in the plastic zone with shear yield $k = \sigma_y / \sqrt{3}$. |
| A-AUT-03 | **Purely elastic unloading** (Lamé) from the autofrettage pressure; reverse yielding (Bauschinger effect) is not modelled. |
| A-AUT-04 | The autofrettage pressure must lie between initial-yield pressure and full-yield pressure; outside that range the solver raises `ValidationError`. |
| A-AUT-05 | **Axial simplification for the working safety-factor estimate:** axial stress is the closed-end elastic working-pressure stress. Residual axial stress is omitted from this calculation. This simplification has not been independently validated for the autofrettage loading/unloading cycle. |
| A-AUT-06 | **Bore-only assessment:** the reported autofrettage safety factor is evaluated at the inner radius. The implementation does not search the wall for the maximum equivalent stress or minimum safety factor. |
| A-AUT-07 | **Elastic reloading assumed:** working-pressure stresses are elastically superimposed on residual stresses. Further plastic redistribution during reloading is not modelled. |

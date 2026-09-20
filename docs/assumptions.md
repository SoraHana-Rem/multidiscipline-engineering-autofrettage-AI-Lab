# Document 3: `docs/assumptions.md`

```markdown
# Assumptions Register: Pressure Vessel Analysis

| Field | Value |
| :--- | :--- |
| Document | `docs/assumptions.md` |
| Status | Finalized for Baseline / Capstone Template |
| Related | `docs/requirements.md`, `docs/design.md` |

Each assumption has an ID. If physical operational conditions depart from an assumption, system results are invalid.

## 1. Physics & Material Assumptions

### 1.1 Material

| ID | Assumption | Literature Reference |
| :--- | :--- | :--- |
| A-MAT-01 | **Isotropic** material: properties are uniform in all directions. Composites and anisotropic materials are out of scope. | Hearn, Vol. 1, Ch. 1 |
| A-MAT-02 | **Homogeneous** material with no microstructural defects, voids, or cracks. | Hearn, Vol. 1, Ch. 1 |
| A-MAT-03 | **Linear elastic** behaviour governed by Hooke's Law up to yield. Plastic deformation is not modelled. | Hearn, Vol. 1, Ch. 1 |
| A-MAT-04 | **Ductile** material: the von Mises (Distortion Energy) yield criterion applies. Brittle material criteria (e.g., Rankine/Tresca) are excluded. | Hearn, Vol. 1, Ch. 15 |
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
| A-LOD-03 | **Closed-end condition:** Axial pressure load is carried by wall giving $\sigma_L = \frac{P\,r_i}{2t}$ (thin) and $\sigma_L = \frac{P a^2}{b^2 - a^2}$ (thick). | Hearn, Vol. 1, Ch. 10 |
| A-LOD-04 | Thermal stresses, aerodynamic forces, and support loads are excluded. | Hearn, Vol. 1, Ch. 10 |
| A-LOD-05 | **Autofrettage prestress excluded:** Residual stress fields resulting from plastic pre-expansion (autofrettage) are out of scope for this baseline module. | Hearn, Vol. 2 |

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
| AI-7 | Generated code **must not** silently clamp, coerce, default, or repair invalid inputs. |
| AI-8 | `bool` values must be rejected, and `NaN` / `inf` caught at input boundaries. |
| AI-9 | Validation belongs in `src/validation/` only; physics core functions remain pure. |
| AI-10 | No magic numbers in calculation code; all configuration constants must reside in `src/config/limits.py`. |
| AI-2 | Functions require standard Python type hints and NumPy-style docstrings with explicit units. |
| AI-3 | Every generated function must be accompanied by a corresponding `pytest` case referencing a `REQ-` ID. |
| AI-13 | The AI tool must run `pytest` and report actual execution results. It must not claim tests pass without running them. |
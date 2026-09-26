# Engineering Reference: Week 6 Autofrettage & Elastic-Plastic Mechanics

## 1. Governing Equations & Formulations

### Plastic Radius ($r_p$) Root Formulation
Under von Mises / Tresca elastic-perfectly plastic assumptions, the autofrettage pressure $P_{auto}$ required to propagate the plastic zone to radius $r_p$ ($r_i < r_p < r_o$) is:

$$P_{auto}(r_p) = \frac{\sigma_y}{\sqrt{3}} \left[ 1 - \left(\frac{r_p}{r_o}\right)^2 + 2 \ln\left(\frac{r_p}{r_i}\right) \right]$$

### Stress Fields & Residual Stress Superposition
Elastic recovery during depressurization subtracts the Lamé unloading stresses from the plastic loading stress state:

$$\sigma_{r, res}(r) = \sigma_{r, load}(r) - \sigma_{r, unload}(r)$$
$$\sigma_{\theta, res}(r) = \sigma_{\theta, load}(r) - \sigma_{\theta, unload}(r)$$

---

## 2. Academic & Technical References

1. **Hill, R. (1950).** *The Mathematical Theory of Plasticity*. Oxford University Press, Oxford. 
   - *Primary reference for elastic-plastic boundary conditions and thick-walled cylinder expansion under internal pressure.*

2. **Chakrabarty, J. (2006).** *Theory of Plasticity* (3rd ed.). Butterworth-Heinemann.
   - *Detailed formulations for Tresca vs. von Mises yield criterion propagation and residual stress superposition in autofrettaged pressure vessels.*

3. **Bland, D. R. (1956).** "Elasto-Plastic Thick-Walled Tubes of Work-Hardening Material Subject to Internal and External Pressures and to Temperature Gradients." *Journal of the Mechanics and Physics of Solids*, 4(4), 209-229.
   - *Classical stress profiles for loading, unloading, and thermal/mechanical coupling in high-pressure cylinders.*

4. **ASME Boiler and Pressure Vessel Code (BPVC), Section VIII, Division 3.** *Alternative Rules for Construction of High Pressure Vessels*.
   - *Industry design standard for autofrettage design limits, fatigue lifecycle evaluation, and reverse yield guardrails.*

5. **Parker, A. P. (2001).** "Autofrettage of High Pressure Cylinders." *International Journal of Pressure Vessels and Piping*, 78(11-12), 807-815.
   - *Comprehensive review of residual stress distributions, Bauschinger effect considerations, and fatigue life enhancements in thick-walled tubes.*
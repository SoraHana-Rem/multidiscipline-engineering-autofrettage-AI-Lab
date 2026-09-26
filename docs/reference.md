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



   week7:
   ## 4. Linear Elastic Fracture Mechanics (LEFM) & Paris Law

### Stress Intensity Factor ($K_I$)
For an internal radial surface crack of depth $a$, the Mode-I Stress Intensity Factor under net hoop stress $\sigma_{\theta}$ is:

$$K_I = Y \cdot \sigma_{\theta} \cdot \sqrt{\pi a}$$

where $Y \approx 1.12$ is the boundary correction factor for an inner-bore surface crack.

### Critical Crack Depth ($a_c$)
Fast fracture occurs when $K_{I, \text{max}} = K_{Ic}$ (Material Fracture Toughness):

$$a_c = \frac{1}{\pi} \left( \frac{K_{Ic}}{Y \cdot \sigma_{\text{max}}} \right)^2$$

### Paris Law Fatigue Crack Growth
The rate of fatigue crack propagation per operational pressure cycle ($N$) is given by:

$$\frac{da}{dN} = C (\Delta K)^m \implies N_f = \int_{a_i}^{a_c} \frac{da}{C \left( Y \Delta\sigma \sqrt{\pi a} \right)^m}$$

---

### Academic & Technical References (Fracture Mechanics)
1. **Paris, P., & Erdogan, F. (1963).** "A Critical Analysis of Crack Propagation Laws." *Journal of Basic Engineering*, 85(4), 528-534.
2. **Tada, H., Paris, P. C., & Irwin, G. R. (2000).** *The Stress Analysis of Cracks Handbook* (3rd ed.). ASME Press.
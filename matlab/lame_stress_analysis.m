% Thick-Walled Pressure Vessel - Lamé Stress Distribution (Ground Truth)
clear; clc;

% Input Parameters
r_i = 0.10;       % Inner radius (m)
r_o = 0.15;       % Outer radius (m)
P_i = 100e6;      % Internal pressure (Pa - 100 MPa)
P_o = 0;          % External pressure (Pa)

% Radial evaluation grid across wall thickness
r = linspace(r_i, r_o, 100);

% Lamé Analytical Equations
denom = r_o^2 - r_i^2;
sigma_r = ((P_i*r_i^2 - P_o*r_o^2) / denom) - (((P_i - P_o)*r_i^2*r_o^2) ./ (r.^2 * denom));
sigma_t = ((P_i*r_i^2 - P_o*r_o^2) / denom) + (((P_i - P_o)*r_i^2*r_o^2) ./ (r.^2 * denom));

% Output boundary stress metrics in MPa
fprintf('=== Lamé Stress Analytical Baseline ===\n');
fprintf('Inner Radius (r = %.2f m):\n', r_i);
fprintf('  Radial Stress  (sigma_r): %6.2f MPa\n', sigma_r(1)/1e6);
fprintf('  Hoop Stress    (sigma_t): %6.2f MPa\n', sigma_t(1)/1e6);
fprintf('Outer Radius (r = %.2f m):\n', r_o);
fprintf('  Radial Stress  (sigma_r): %6.2f MPa\n', sigma_r(end)/1e6);
fprintf('  Hoop Stress    (sigma_t): %6.2f MPa\n', sigma_t(end)/1e6);
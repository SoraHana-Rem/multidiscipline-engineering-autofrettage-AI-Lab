%% export_reference_data.m
% Independent MATLAB computation of Lamé stresses for Python cross-validation.
clear; clc;

% Geometry & Load Parameters
ri  = 0.10;     % m
ro  = 0.15;     % m
P_i = 10e6;     % Pa
P_o = 0;        % Pa
n   = 100;      % radial points

% Lamé Exact Solution
r = linspace(ri, ro, n)';
A = (P_i * ri^2 - P_o * ro^2) / (ro^2 - ri^2);
B = (P_i - P_o) * ri^2 * ro^2 / (ro^2 - ri^2);

sigma_r_matlab     = A - B ./ r.^2;
sigma_theta_matlab = A + B ./ r.^2;

% Assertions
assert(abs(sigma_r_matlab(1) + P_i) < 1e-3, 'Boundary condition at r_i failed');
assert(abs(sigma_r_matlab(end) + P_o) < 1e-3, 'Boundary condition at r_o failed');

% Export Table
T = table(r, repmat(ri,n,1), repmat(ro,n,1), repmat(P_i,n,1), repmat(P_o,n,1), ...
    sigma_r_matlab, sigma_theta_matlab, ...
    'VariableNames', {'r','r_i','r_o','P_i','P_o','sigma_r_matlab','sigma_theta_matlab'});

out_path = fullfile(fileparts(mfilename('fullpath')), '..', 'src', 'validation', 'matlab_reference.csv');
writetable(T, out_path);
fprintf('Successfully generated reference CSV at: %s\n', out_path);
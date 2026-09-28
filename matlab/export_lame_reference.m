%% export_lame_reference.m
% Writes MATLAB Lame reference data for the Python cross-check
% (src/validation/cross_validate.py). Units: SI (m, Pa).
%
% MATLAB Online workflow: run this script, download matlab_reference.csv from
% the Current Folder panel, and place it in src/validation/ in the repository.
% Desktop MATLAB: set the current folder to the repository root and change the
% writetable path to 'src/validation/matlab_reference.csv'.
clear; clc;

ri  = 0.10;    % m   inner radius
ro  = 0.15;    % m   outer radius
p_i = 10e6;    % Pa  internal pressure
p_o = 0;       % Pa  external pressure
N   = 100;     % radial points

r   = linspace(ri, ro, N).';
den = ro^2 - ri^2;
A   = (p_i*ri^2 - p_o*ro^2)/den;
B   = (p_i - p_o)*ri^2*ro^2/den;
sr  = A - B./r.^2;    % radial stress (Pa)
st  = A + B./r.^2;    % hoop stress (Pa)

T = table(r, repmat(ri,N,1), repmat(ro,N,1), repmat(p_i,N,1), repmat(p_o,N,1), sr, st, ...
    'VariableNames', {'r','r_i','r_o','P_i','P_o','sigma_r_matlab','sigma_theta_matlab'});

writetable(T, 'matlab_reference.csv');
fprintf('Wrote matlab_reference.csv (%d rows)\n', N);
%% lame_stress_analysis.m
% Baseline verification: thick-walled cylinder under internal pressure (Lame)
% Closed ends, linear-elastic, isotropic, axisymmetric, small strain.
% Units: SI throughout (m, Pa, N/m). Reported in mm / MPa / um.
clear; clc;

%% ---- Inputs ----
ri  = 0.050;    % m    inner radius (50 mm)
ro  = 0.100;    % m    outer radius (100 mm)
p_i = 100e6;    % Pa   internal pressure (100 MPa)
p_o = 0;        % Pa   external pressure
E   = 200e9;    % Pa   Young's modulus
nu  = 0.30;     % -    Poisson's ratio
N   = 2001;     % -    radial grid points

%% ---- Tolerances ----
tol_bc    = 1e-9;   % relative, boundary-condition residual
tol_eq    = 1e-5;   % relative, equilibrium residual
tol_force = 1e-6;   % relative, hoop force balance
tol_hand  = 1e-4;   % relative, code vs hand calc

%% ---- Lame solution ----
den = ro^2 - ri^2;
A   = (p_i*ri^2 - p_o*ro^2)/den;               % Pa
B   = (p_i - p_o)*ri^2*ro^2/den;               % Pa*m^2
sz  = A;                                       % Pa, closed-end axial stress

r   = linspace(ri, ro, N);
sr  = A - B./r.^2;                              % radial stress
st  = A + B./r.^2;                              % hoop stress
ur  = r/E .* (st - nu*(sr + sz));              % radial displacement (m)
vm  = sqrt(0.5*((st-sr).^2 + (sr-sz).^2 + (sz-st).^2)); % von Mises
tr  = max(abs([st-sr; sr-sz; sz-st]), [], 1);     % Tresca

%% ---- Hand-calc values (MPa, um) at r_i and r_o ----
hand.sr = [-100.000,   0.000];
hand.st = [ 166.667,  66.667];
hand.sz = [  33.333,  33.333];
hand.ur = [  46.667,  28.333];   % um
hand.vm = [ 230.940,  57.735];

%% ---- Checks ----
res = struct('name', {}, 'value', {}, 'tol', {});

% 1) Boundary conditions
res(end+1) = struct('name','BC sigma_r(r_i) = -p_i', 'value',abs(sr(1) + p_i)/p_i, 'tol',tol_bc);
res(end+1) = struct('name','BC sigma_r(r_o) = -p_o', 'value',abs(sr(end) + p_o)/p_i, 'tol',tol_bc);

% 2) Radial equilibrium: d(sr)/dr + (sr - st)/r = 0
dsr = gradient(sr, r);
eq  = dsr + (sr - st)./r;
k   = 2:N-1;
res(end+1) = struct('name','Equilibrium residual', ...
    'value', max(abs(eq(k)))/max(abs(st(k)./r(k))), 'tol', tol_eq);

% 3) Hoop force balance: int(sigma_theta dr) = p_i*ri - p_o*ro
F_num   = trapz(r, st);
F_exact = p_i*ri - p_o*ro;
res(end+1) = struct('name','Hoop force balance', ...
    'value', abs(F_num - F_exact)/abs(F_exact), 'tol', tol_force);

% 4) Code vs hand calc at boundaries
idx = [1, N];  lab = {'r_i','r_o'};
for j = 1:2
    i = idx[j];
    cmp = { 'sigma_theta', st(i)/1e6, hand.st(j);
            'sigma_z',     sz/1e6,    hand.sz(j);
            'u_r [um]',    ur(i)*1e6, hand.ur(j);
            'von Mises',   vm(i)/1e6, hand.vm(j) };
    for m = 1:size(cmp,1)
        res(end+1) = struct('name', sprintf('Hand vs code: %s @ %s', cmp{m,1}, lab{j}), ...
            'value', abs(cmp{m,2} - cmp{m,3})/abs(cmp{m,3}), 'tol', tol_hand);
    end
end

%% ---- Report ----
fprintf('A = %.4f MPa, B = %.4e Pa*m^2, sigma_z = %.4f MPa\n\n', A/1e6, B, sz/1e6);
fprintf('%-14s %10s %10s %10s %10s %10s %10s\n', 'Location', ...
        'sig_r[MPa]','sig_t[MPa]','sig_z[MPa]','u_r[um]','vM[MPa]','Tresca');
for j = 1:2
    i = idx(j);
    fprintf('%-14s %10.3f %10.3f %10.3f %10.3f %10.3f %10.3f\n', lab{j}, ...
        sr(i)/1e6, st(i)/1e6, sz/1e6, ur(i)*1e6, vm(i)/1e6, tr(i)/1e6);
end
fprintf('\n%-42s %12s %10s  %s\n', 'Check', 'Rel. error', 'Tol', 'Result');
allpass = true;
for q = 1:numel(res)
    ok = res(q).value <= res(q).tol;  allpass = allpass && ok;
    fprintf('%-42s %12.3e %10.1e  %s\n', res(q).name, res(q).value, res(q).tol, ...
        ternary(ok,'PASS','FAIL'));
end
fprintf('\nOVERALL: %s\n', ternary(allpass,'ALL CHECKS PASSED','REVIEW REQUIRED'));

function s = ternary(c, a, b)
    if c, s = a; else, s = b; end
end
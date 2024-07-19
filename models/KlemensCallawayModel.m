% Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved
function [k] = KlemensCallawayModel(C,Rl,Nl,Temp,S2)
% Input:
% C - concentration of defects [1/atoms] for each defect, input as a vector in the
% order of [V_U V_O U_I O_I] (read as uranium (U) vacancy (V), oxygen (O)
% vacancy, uranium interstital (I), oxygen interstital).
% Temp - temperature of the material [C] (not irradiation temperatures -
% this is used for post irradiation examination calculations when the
% material was irradiated at one temperature but is now a different
% temperature during measurement.
% Rl - size of dislocation loops [nm]
% Nl - density of dislocation loops [1/atoms]
% S2 - scattering cross sections of defects [~] given as as a vector
% for each defect type, in similar format to C.
% ------------------------------------------
% Output:
% k - thermal conductivity [W/m-K]

Temp = Temp+273.15; % Kel. material temperature
hbar = 1.054e-34; % m^2-kg/s
kb_j = 1.380649e-23; % J/K
TD = 395; % K
vs = 2644; % m/s
B = 1.70305604881574e-18; % K/s
N = 3; % at
lat = .541e-9; % m
Vo = 3.98e-29; % m^3
NN = 1000; % integration discretization
a = 5.470649999e-10; % m
omega = a^3/4; % m^3
wd = (6*pi^2*vs^3/Vo)^(1/3); % THz

w = wd/NN:wd/NN:wd;

gammai = 0.0664165932375061; % ~
gru = 1.8;
% S2i = [22.6 7.49 16.6 7.68]; % scattering parameters
x = hbar*w/kb_j/Temp;

Nl = Nl/omega; % [1/m^3]
Rl = Rl*1e-9; % [m]
gamma = sum(C.*S2);

C_sh = kb_j.*x.^2.*exp(x)./(1-exp(x)).^2; % Specific Heat
D = w.^2/(2*pi^2*vs.^3); % Density of State
tau_3ph = B*w.^2*Temp*exp(-TD/(3*Temp)); % 3-Phonon Scattering
tau_i = Vo/(4*pi*N*vs^3)*gammai*w.^4; % Impurities Scattering
tau_m = Vo/(4*pi*N*vs^3)*gamma*w.^4; % Point Defect Scattering
tau_l = .7*a^2*gru^2*(pi*Rl^2*Nl)*w.^2/vs; % Loop Scattering

tauinv = tau_3ph + tau_i + tau_m + tau_l; % point defects + impurities + loops
tau = 1./tauinv;

kmin = 1.0;
lmina = kmin/0.49;
for jj = 1:size(tau,2)
    lmin = lmina*a; % one phonon wavelength [m]
    mfp = tau(jj)*vs; % mean free path of phonon at freq (w) [m]
    if (mfp<lmin)
        tau(jj) = lmin/vs; % Scattering time to mins conductivity
    end
end

kint = kb_j.*vs.^2.*tau.*D;
k = sum(kint,2).*wd./NN;

end

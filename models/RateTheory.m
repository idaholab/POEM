% Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved
function [Npds,Rl,Nl] = RateTheory(Em,D0,Tirr,dmg,doserate,a,roM)
% Input:
% Em - migration energies [eV] for each defect, input as a vector in the
% order of [V_U V_O U_I O_I] (read as uranium (U) vacancy (V), oxygen (O)
% vacancy, uranium interstital (I), oxygen interstital).
% D0 - diffusion prefactors [unitless] same vector input as listed above
% Tirr - irradiation temperauture [C]
% dmg - irradiation damage [dpa]
% dose - irradiation dose [dpa/s]
% ------------------------------------------
% Output:
% Npds - point defect concentrations [1/atoms] for each defect, output as a
% vector in similar format to migration energies
% Rl - size of dislocation loops [nm]
% Nl - density of dislocation loops [1/atoms]

% --------------- Dmg / Temp ---------------
T = Tirr+273.15; % Kel. Irr. Temp
to = 0.00114942528735632*.1;tspan = [to dmg/doserate];
% a = 547.127*1e-10;  % cm
omega = a^3/4; % cm^3
ro = roM*a; % cm
beta = 84*omega/a^2; % cm
b = a/sqrt(3); % cm
kb_ev = 8.617333262145e-5; % eV/K
% --------------- Production Rates ---------------
Gtot = doserate/omega; % [dpa/s]/[cm^3] = [1/cm^3*s]
Defectratio = 1.34; % O/U
GO = Gtot*(1-1/(1+Defectratio));GU = Gtot*(1/(1+Defectratio));
GvU = GU;GvO = GO;GUi = GU;GOi = GO;
% --------------- Prefactors ---------------
DvUi = D0(1);DvOi = D0(2);DiUi = D0(3);DiOi = D0(4);EmvU = Em(1);...
    EmvO= Em(2);EmUi = Em(3);EmOi = Em(4);
% --------------- Initial Values  ---------------
n = 6; % diatomic N = 6, monoatomic N = 2
xo(1) = GU*to; % concentration initial value are Go*t_o (C_o = C_i)
xo(2) = GO*to;
xo(3) = xo(1);
xo(4) = xo(2);
xo(5) = 1e-12/omega;
xo(6) = sqrt(n*omega/(pi*b)); % initial loop radii
% --------------- Integration ---------------
[t,y] = ode15s(@Diff,tspan,xo); % (1:5) [1/cm^3] / (6) [cm]
yy = y*omega; % (1:5) & [1/At]
dpa = t*doserate; % dpa
Npds = yy(end,1:4); % [1/At]
Nl = yy(end,5); % [1/At]
Rl = y(end,6)*1e7; % [cm] --> [nm]
   function xdot = Diff(t,x)
        % CENTIMETERS
        DvU = DvUi*exp(-EmvU/(kb_ev*T)); % cm^2/s
        DiU = DiUi*exp(-EmUi/(kb_ev*T)); % cm^2/s
        DvO = DvOi*exp(-EmvO/(kb_ev*T)); % cm^2/s
        DiO = DiOi*exp(-EmOi/(kb_ev*T)); % cm^2/s
        % --------------- Flux ---------------
        jli = 1/(ro*log(8*x(6)/ro))*((DiU*x(3)*DiO*x(4))/(2*DiU*x(3)+(DiO*x(4))));
        jlv = 1/(ro*log(8*x(6)/ro))*((DvU*x(1)*DvO*x(2))/(2*DvU*x(1)+(DvO*x(2))));
        jii = (DiU*x(3)*x(3)*DiO*x(4)*x(4))/(2*DiU*x(3)*x(3)+(DiO*x(4)*x(4)));
        % --------------- Loops ---------------
        xdot(5) = beta*jii;
        xdot(6) = 3*omega*(2*pi*ro/b)*(jli-jlv); % - x(6)*beta*jii/(2*x(5));

        if (xdot(6)<0) && (x(6) < (1.99*a))
            jli = 0;
            jlv = 0;
            xdot(6) = 0;
        end
        % --------------- Concentration (Growth) ---------------
        xdot(1) = GvU;
        xdot(2) = GvO;
        xdot(3) = GUi;
        xdot(4) = GOi;
        % --------------- Concentration (Recombination) ---------------
        xdot(1) = xdot(1) - (omega/a^2)*(48*DiU+48*DvU)*x(1)*x(3);
        xdot(2) = xdot(2) - (omega/a^2)*(36*DiO+24*DvO)*x(2)*x(4);
        xdot(3) = xdot(3) - (omega/a^2)*(48*DiU+48*DvU)*x(1)*x(3);
        xdot(4) = xdot(4) - (omega/a^2)*(36*DiO+24*DvO)*x(2)*x(4);
        % --------------- Concentration (Loop Sinks) ---------------
        xdot(1) = xdot(1) - jlv*pi*ro*2*pi*x(6)*x(5);
        xdot(2) = xdot(2) - 2*jlv*pi*ro*2*pi*x(6)*x(5);
        xdot(3) = xdot(3) - jli*pi*ro*2*pi*x(6)*x(5);
        xdot(4) = xdot(4) - 2*jli*pi*ro*2*pi*x(6)*x(5);
        % --------------- Concentration (Loop Nucl.) ---------------
        xdot(3) = xdot(3) - beta*jii;
        xdot(4) = xdot(4) - 2*beta*jii;
        xdot = xdot';
   end
end

% Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved
% Sample function call
clear all
close all

% Plot the dislocation loop radius and density at 1 dpa, as a function of irradiation
% temperature (Rate Theory temperature)
N = 100;
irrT = 0:1e3/N:1e3;
Em = [5 2.1 2.6 1];
D0 = [0.65 0.02 0.01 0.01];
% damage = 1;
% using RAVEN generic interface to perturb model inputs to allow parametric study
damage = $RAVEN-damage$;
doserate = 1e-5;
a = 5.4713e-08;
roM = 4;
for i = 1:N + 1
    [C,Rl,Nl] = RateTheory(Em,D0,irrT(i),damage,doserate,a,roM);
    Ci(1:4,i) = C;RL(i) = Rl;NL(i) = Nl;
    k(i) = KlemensCallawayModel(C,Rl,Nl,600,[22.6 7.49 16.6 7.68]);
end

title = {'irrT', 'RL', 'NL', 'k'};
data = [irrT.', RL', NL', k'];
table = array2table(data);
table.Properties.VariableNames(1:4) = title;
filename = 'out_sauq.csv';
writetable(table, filename);

exit()



%% Omni DrugAssist Molecular Reasoning (Prolog)
%% Compute Layer: Drug-likeness rule engine.
%% Ref: blazerye/DrugAssist
:- module(omni_drugassist, [drug_like/4, violation_count/5]).
drug_like(MW, LogP, HBD, HBA) :-
    MW =< 500, LogP =< 5, HBD =< 5, HBA =< 10.
violation_count(MW, LogP, HBD, HBA, Count) :-
    findall(1, (MW > 500 ; LogP > 5 ; HBD > 5 ; HBA > 10), Vs),
    length(Vs, Count).

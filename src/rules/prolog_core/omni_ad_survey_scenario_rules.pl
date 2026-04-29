% Omni AD Survey Scenario Rules (Prolog)
% Rule Layer: Autonomous Driving scenario boundary validation.

% Facts
scenario_type(highway).
scenario_type(urban).
scenario_type(pedestrian_crossing).

% Rules
valid_speed_limit(highway, Speed) :- Speed =< 120, Speed >= 60.
valid_speed_limit(urban, Speed) :- Speed =< 50, Speed >= 0.
valid_speed_limit(pedestrian_crossing, Speed) :- Speed =< 30, Speed >= 0.

% Monadic-style logic predicate
validate_ad_scenario(Type, Speed, Result) :-
    scenario_type(Type),
    valid_speed_limit(Type, Speed),
    Result = ok;
    Result = error(bounds_violation).

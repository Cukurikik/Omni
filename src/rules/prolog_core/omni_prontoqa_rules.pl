// Omni ProntoQA Rules (Prolog)
// Rules Layer: Formal deductive rules for chain-of-thought validation.
// Ref: asaparov/prontoqa

is_a(X, Y) :- direct_is_a(X, Y).
is_a(X, Y) :- direct_is_a(X, Z), is_a(Z, Y).

validate_chain([]).
validate_chain([step(Premise, Conclusion, Rule) | Rest]) :-
    known(Premise),
    apply_rule(Rule, Premise, Conclusion),
    assert(known(Conclusion)),
    validate_chain(Rest).

apply_rule(modus_ponens, P, C) :- implies(P, C).

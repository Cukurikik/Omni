% Omni Symbolic Knowledge Base (Prolog)
% Deterministic logic inference for Neurosymbolic RAG.

% Base Facts
omni_layer(system).
omni_layer(network).
omni_layer(compute).
omni_layer(interface).

% Rules
is_safe_dependency(LayerA, LayerB) :-
    omni_layer(LayerA),
    omni_layer(LayerB),
    LayerA \= LayerB,
    (LayerA = interface -> LayerB \= system ; true).

% Strict query execution simulating a Monadic Result
validate_architecture(ReqA, ReqB, Result) :-
    ( is_safe_dependency(ReqA, ReqB) ->
        Result = ok(safe)
    ;
        Result = err("Violation of Omni Domain Segregation")
    ).

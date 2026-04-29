% OmniSymbolicReasoner - OMNI Compute Layer
%
% Prolog rules for symbolic reasoning and constraint deduction.
% Used by Neurosymbolic AI engines in OMNI.

% Facts: Define basic domain hierarchy
is_layer(system).
is_layer(compute).
is_layer(network).
is_layer(domain).
is_layer(ui).

language_layer(rust, system).
language_layer(c_plus_plus, system).
language_layer(python, compute).
language_layer(julia, compute).
language_layer(go, network).
language_layer(typescript, ui).

% Rules: Monadic compliance requirement
requires_monad(Language) :-
    language_layer(Language, system).
requires_monad(Language) :-
    language_layer(Language, network).

% Rule: Zero-Copy dependency mapping
can_pass_zero_copy(LangA, LangB) :-
    language_layer(LangA, system),
    language_layer(LangB, system).

% Rule: Security Policy
allow_direct_call(LangA, LangB) :-
    language_layer(LangA, compute),
    language_layer(LangB, system),
    requires_monad(LangA),
    requires_monad(LangB).

% Inference engine entry point
check_architecture_safety(Source, Target, Result) :-
    ( allow_direct_call(Source, Target) ->
        Result = 'safe_monadic_call'
    ; Result = 'requires_bridge_validation' ).

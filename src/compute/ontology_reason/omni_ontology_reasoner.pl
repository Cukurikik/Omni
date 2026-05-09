%% @omni-layer Compute | @omni-lang Prolog | @omni-batch 17
%% @omni-description Ontology reasoner: Prolog-based knowledge base with
%% taxonomic inference, transitive closure, and semantic query resolution.

:- module(omni_ontology_reasoner, [
    assert_concept/3,
    assert_relation/3,
    is_a/2,
    has_property/2,
    related_to/3,
    transitive_ancestor/2,
    all_ancestors/2,
    common_ancestor/3,
    classify_concept/2,
    query_by_type/2,
    explain_relation/3
]).

%% Dynamic knowledge base
:- dynamic concept/3.        %% concept(Name, Type, Confidence)
:- dynamic relation/3.       %% relation(Subject, Predicate, Object)
:- dynamic taxonomy/2.       %% taxonomy(Child, Parent)

%% Assert a new concept
assert_concept(Name, Type, Confidence) :-
    Confidence >= 0, Confidence =< 1,
    member(Type, [entity, process, attribute, relation, event, state]),
    assertz(concept(Name, Type, Confidence)).

%% Assert a relation
assert_relation(Subject, Predicate, Object) :-
    member(Predicate, [is_a, part_of, has_property, causes, precedes, similar_to]),
    assertz(relation(Subject, Predicate, Object)),
    (Predicate == is_a -> assertz(taxonomy(Subject, Object)) ; true).

%% Check IS-A relationship
is_a(Child, Parent) :- taxonomy(Child, Parent).
is_a(Child, Ancestor) :- taxonomy(Child, Mid), is_a(Mid, Ancestor).

%% Check HAS-PROPERTY
has_property(Concept, Property) :-
    relation(Concept, has_property, Property).
has_property(Concept, Property) :-
    is_a(Concept, Parent),
    relation(Parent, has_property, Property).  %% inherited

%% General relation query
related_to(Subject, Predicate, Object) :-
    relation(Subject, Predicate, Object).

%% Transitive ancestor chain
transitive_ancestor(X, Y) :- taxonomy(X, Y).
transitive_ancestor(X, Y) :- taxonomy(X, Z), transitive_ancestor(Z, Y).

%% All ancestors of a concept
all_ancestors(Concept, Ancestors) :-
    findall(A, transitive_ancestor(Concept, A), Ancestors).

%% Common ancestor of two concepts
common_ancestor(X, Y, Ancestor) :-
    transitive_ancestor(X, Ancestor),
    transitive_ancestor(Y, Ancestor).

%% Classify a new term by similarity to existing concepts
classify_concept(Term, Classification) :-
    concept(Term, Type, Conf),
    Classification = classification(term=Term, type=Type, confidence=Conf).

%% Query all concepts by type
query_by_type(Type, Results) :-
    findall(concept(Name, Type, Conf), concept(Name, Type, Conf), Results).

%% Explain why two concepts are related
explain_relation(X, Y, Explanation) :-
    relation(X, Pred, Y),
    Explanation = direct(X, Pred, Y).
explain_relation(X, Y, Explanation) :-
    is_a(X, Y),
    Explanation = taxonomic(X, is_a, Y).
explain_relation(X, Y, Explanation) :-
    relation(X, Pred, Z),
    related_to(Z, _, Y),
    Explanation = transitive(X, Pred, Z, Y).

%% Pre-loaded ontology for AI domain
:- assert_concept('Machine Learning', process, 0.95).
:- assert_concept('Neural Network', entity, 0.92).
:- assert_concept('Transformer', entity, 0.97).
:- assert_concept('Attention', attribute, 0.91).
:- assert_concept('Deep Learning', process, 0.90).
:- assert_relation('Neural Network', is_a, 'Machine Learning').
:- assert_relation('Transformer', is_a, 'Neural Network').
:- assert_relation('Transformer', has_property, 'Attention').
:- assert_relation('Deep Learning', is_a, 'Machine Learning').

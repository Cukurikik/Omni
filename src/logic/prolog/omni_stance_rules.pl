% OMNI Framework - Prolog Logic for Stance Detection KE-MLM
% Determines overall stance based on extracted entities and relationships

% Facts extracted from Knowledge Enhanced MLM
entity(climate_change).
entity(carbon_tax).

% Base sentiments provided by the Ruformers/FinBERT engine
sentiment(user123, climate_change, positive).
sentiment(user123, carbon_tax, negative).

% Relationships defining ideological alignment
supports_policy(climate_change, carbon_tax).

% Rules
% If a user is positive about a concept, but negative about its supporting policy, there is a contradiction.
contradictory_stance(User, Concept, Policy) :-
    sentiment(User, Concept, positive),
    supports_policy(Concept, Policy),
    sentiment(User, Policy, negative).

% Overall stance classification
stance(User, Concept, 'Favor') :- sentiment(User, Concept, positive).
stance(User, Concept, 'Against') :- sentiment(User, Concept, negative).
stance(User, Concept, 'Contradictory') :- contradictory_stance(User, Concept, _).

% Query Example:
% ?- stance(user123, climate_change, Stance).

---- MODULE OmniProntoQASpec ----
\* Formal Layer: TLA+ spec for ProntoQA chain-of-thought validity.
\* Ref: asaparov/prontoqa

EXTENDS Integers, FiniteSets

VARIABLES known_facts, chain_valid

Init ==
    /\ known_facts = {"premise_A", "premise_B"}
    /\ chain_valid = FALSE

ApplyRule(premise, conclusion) ==
    /\ premise \in known_facts
    /\ known_facts' = known_facts \cup {conclusion}
    /\ chain_valid' = TRUE

Spec == Init /\ [][(\E p, c \in STRING : ApplyRule(p, c))]_<<known_facts, chain_valid>>

Safety == chain_valid => Cardinality(known_facts) >= 2
====

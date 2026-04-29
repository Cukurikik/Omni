---------------- MODULE OmniSimplyRetrieveSpec ----------------
\* Formal Verification of Retrieval-Centric Logic
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS 
    Documents,
    Queries,
    MaxRetrievalCount

VARIABLES 
    retrieved_set,
    query_queue

TypeInvariant ==
    /\ retrieved_set \subseteq Documents
    /\ query_queue \in Seq(Queries)

Init ==
    /\ retrieved_set = {}
    /\ query_queue = <<>>

Retrieve(q) ==
    /\ query_queue /= <<>>
    /\ Head(query_queue) = q
    /\ Cardinality(retrieved_set) < MaxRetrievalCount
    /\ retrieved_set' = retrieved_set \cup { CHOOSE d \in Documents : TRUE } \* Abstracted relevance
    /\ query_queue' = Tail(query_queue)

Next == 
    \E q \in Queries : Retrieve(q)

Spec == Init /\ [][Next]_<<retrieved_set, query_queue>>

=============================================================================

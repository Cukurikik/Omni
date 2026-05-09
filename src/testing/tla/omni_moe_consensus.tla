---- MODULE OmniMoEConsensus ----
(* OMNI MOTHER: TLA+ Spec for Leader Election *)

EXTENDS Integers

VARIABLES leader, nodes

Init == 
    /\ leader = "none"
    /\ nodes = {"n1", "n2", "n3"}

ElectLeader(n) == 
    /\ leader = "none"
    /\ n \in nodes
    /\ leader' = n
    /\ nodes' = nodes

Next == \E n \in nodes : ElectLeader(n)

Spec == Init /\ [][Next]_<<leader, nodes>>

====

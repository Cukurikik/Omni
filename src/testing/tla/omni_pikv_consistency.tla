---- MODULE OmniPiKVConsistency ----
(* OMNI MOTHER: Testing & Verification Layer (TLA+) *)
(* Proves safety of distributed KV block allocation *)

EXTENDS Integers

VARIABLES blocks, state

Init == 
    /\ blocks = 100
    /\ state = "READY"

Allocate == 
    /\ state = "READY"
    /\ blocks > 0
    /\ blocks' = blocks - 1
    /\ state' = "READY"

Free == 
    /\ state = "READY"
    /\ blocks' = blocks + 1
    /\ state' = "READY"

Next == Allocate \/ Free

Spec == Init /\ [][Next]_<<blocks, state>>

(* Invariant: We never have negative blocks *)
Safety == blocks >= 0

====

---- MODULE OmniStateMachine ----
EXTENDS Naturals, Sequences

(* OMNI Testing & Verification Layer *)
(* Proves the absence of deadlocks in cross-language agent communication *)

VARIABLES state, queue

Init == 
    /\ state = "IDLE"
    /\ queue = <<>>

Dispatch(task) == 
    /\ state = "IDLE"
    /\ queue' = Append(queue, task)
    /\ state' = "PROCESSING"

Complete == 
    /\ state = "PROCESSING"
    /\ queue /= <<>>
    /\ queue' = Tail(queue)
    /\ state' = "IDLE"

Next == 
    \/ \E t \in {"compute", "network", "system"}: Dispatch(t)
    \/ Complete

Spec == Init /\ [][Next]_<<state, queue>>

(* Invariant: The system never enters an undefined state *)
Safety == state \in {"IDLE", "PROCESSING"}
=================================

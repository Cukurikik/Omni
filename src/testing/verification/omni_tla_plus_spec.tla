--------------------------- MODULE omni_tla_plus_spec ---------------------------
EXTENDS Integers, Sequences, TLC

(* OMNI Testing & Verification Layer *)
(* Formal TLA+ specification to verify the safety and liveness of the OMNI Gossip Protocol *)

CONSTANTS Nodes, MaxVersion

VARIABLES state, version, messages

TypeOK == 
    /\ state \in [Nodes -> {"active", "syncing", "offline"}]
    /\ version \in [Nodes -> 0..MaxVersion]
    /\ messages \in SUBSET [src: Nodes, dst: Nodes, v: 0..MaxVersion]

Init == 
    /\ state = [n \in Nodes |-> "active"]
    /\ version = [n \in Nodes |-> 0]
    /\ messages = {}

(* Node n1 sends a state update to node n2 *)
Gossip(n1, n2) == 
    /\ state[n1] = "active"
    /\ state[n2] # "offline"
    /\ messages' = messages \cup {[src |-> n1, dst |-> n2, v |-> version[n1]]}
    /\ UNCHANGED <<state, version>>

(* Node n receives a message and updates its version if the received version is newer *)
Receive(n) == 
    \E m \in messages:
        /\ m.dst = n
        /\ m.v > version[n]
        /\ version' = [version EXCEPT ![n] = m.v]
        /\ messages' = messages \ {m}
        /\ UNCHANGED <<state>>

(* A node advances its own state version autonomously (e.g. completes a training step) *)
Advance(n) == 
    /\ state[n] = "active"
    /\ version[n] < MaxVersion
    /\ version' = [version EXCEPT ![n] = version[n] + 1]
    /\ UNCHANGED <<state, messages>>

Next == 
    \/ \E n1, n2 \in Nodes: n1 # n2 /\ Gossip(n1, n2)
    \/ \E n \in Nodes: Receive(n)
    \/ \E n \in Nodes: Advance(n)

(* Safety Property: A node's version never goes backward *)
Safety == \A n \in Nodes: version'[n] >= version[n]

(* Liveness Property: All active nodes eventually reach MaxVersion *)
Liveness == <>(\A n \in Nodes: state[n] = "active" => version[n] = MaxVersion)

Spec == Init /\ [][Next]_<<state, version, messages>> /\ WF_vars(Next)

=============================================================================

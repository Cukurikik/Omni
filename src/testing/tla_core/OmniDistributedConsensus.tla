---- MODULE OmniDistributedConsensus ----
\* OMNI Testing & Verification Layer
\* Formal verification of the underlying state machine running
\* the OMNI cluster multiplexer using TLA+.

EXTENDS Integers, Sequences, TLC

CONSTANTS Nodes, MaxMessages

VARIABLES state, messages

vars == <<state, messages>>

Init ==
    /\ state = [n \in Nodes |-> "follower"]
    /\ messages = <<>>

Send(m) ==
    /\ Len(messages) < MaxMessages
    /\ messages' = Append(messages, m)
    /\ UNCHANGED state

BecomeLeader(n) ==
    /\ state[n] = "follower"
    /\ \A m \in Nodes \ {n} : state[m] # "leader"
    /\ state' = [state EXCEPT ![n] = "leader"]
    /\ Send([type |-> "LEADER_ELECTED", node |-> n])

Follow(n) ==
    /\ state[n] = "follower"
    /\ \E m \in 1..Len(messages) : messages[m].type = "LEADER_ELECTED"
    /\ state' = [state EXCEPT ![n] = "following"]
    /\ UNCHANGED messages

Next == 
    \/ \E n \in Nodes : BecomeLeader(n)
    \/ \E n \in Nodes : Follow(n)

Spec == Init /\ [][Next]_vars

\* Safety Property: There can never be two leaders simultaneously
AtMostOneLeader == 
    \A n1, n2 \in Nodes : 
        (state[n1] = "leader" /\ state[n2] = "leader") => (n1 = n2)

====

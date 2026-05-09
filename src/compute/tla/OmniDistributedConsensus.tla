---------------- MODULE OmniDistributedConsensus ----------------
EXTENDS Naturals, Sequences

VARIABLES state, messages

Init ==
    /\ state = "follower"
    /\ messages = <<>>

BecomeLeader ==
    /\ state = "follower"
    /\ state' = "leader"
    /\ messages' = Append(messages, "HEARTBEAT")

ReceiveHeartbeat ==
    /\ state = "leader"
    /\ messages' = Tail(messages)
    /\ state' = state

Next == 
    \/ BecomeLeader
    \/ ReceiveHeartbeat

Spec == Init /\ [][Next]_<<state, messages>>

=============================================================================

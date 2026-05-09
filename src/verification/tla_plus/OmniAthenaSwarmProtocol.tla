---- MODULE OmniAthenaSwarmProtocol ----
EXTENDS Naturals, Sequences

CONSTANTS Agents, ComputeNodes

VARIABLES agentState, nodeLoad

Init == 
    /\ agentState = [a \in Agents |-> "IDLE"]
    /\ nodeLoad = [n \in ComputeNodes |-> 0]

AssignTask(a, n) ==
    /\ agentState[a] = "IDLE"
    /\ nodeLoad[n] < 10  \* Max load threshold
    /\ agentState' = [agentState EXCEPT ![a] = "COMPUTING"]
    /\ nodeLoad' = [nodeLoad EXCEPT ![n] = @ + 1]

CompleteTask(a, n) ==
    /\ agentState[a] = "COMPUTING"
    /\ agentState' = [agentState EXCEPT ![a] = "IDLE"]
    /\ nodeLoad' = [nodeLoad EXCEPT ![n] = @ - 1]

Next == 
    \E a \in Agents, n \in ComputeNodes :
        \/ AssignTask(a, n)
        \/ CompleteTask(a, n)

Spec == Init /\ [][Next]_<<agentState, nodeLoad>>

\* Liveness property: All agents eventually become idle after computing
EventuallyIdle == \A a \in Agents : (agentState[a] = "COMPUTING") ~> (agentState[a] = "IDLE")

====

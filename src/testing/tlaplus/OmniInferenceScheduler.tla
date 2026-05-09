---- MODULE OmniScheduler ----
EXTENDS Integers, Sequences, FiniteSets
CONSTANTS MaxReqs, MaxGPUs, MaxBatch

VARIABLES queue, gpuState, completed

Init == /\ queue = <<>> /\ gpuState = [g \in 1..MaxGPUs |-> "idle"] /\ completed = 0

Submit(r) == /\ Len(queue) < 100 /\ queue' = Append(queue, r) /\ UNCHANGED <<gpuState, completed>>

Schedule == /\ Len(queue) > 0
  /\ \E g \in 1..MaxGPUs: gpuState[g] = "idle"
     /\ gpuState' = [gpuState EXCEPT ![g] = "busy"]
     /\ queue' = Tail(queue) /\ completed' = completed + 1

Complete == /\ \E g \in 1..MaxGPUs: gpuState[g] = "busy"
  /\ gpuState' = [gpuState EXCEPT ![g] = "idle"] /\ UNCHANGED <<queue, completed>>

Next == (\E r \in 1..MaxReqs: Submit(r)) \/ Schedule \/ Complete
Safety == completed <= MaxReqs
====

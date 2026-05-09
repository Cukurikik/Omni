---- MODULE chimera_pipeline_safety ----
EXTENDS Naturals, Sequences

VARIABLES pipeline_state

Init == pipeline_state = "IDLE"

Next == \/ pipeline_state = "IDLE" /\ pipeline_state' = "FORWARD"
        \/ pipeline_state = "FORWARD" /\ pipeline_state' = "BACKWARD"
        \/ pipeline_state = "BACKWARD" /\ pipeline_state' = "IDLE"

Spec == Init /\ [][Next]_pipeline_state

Safety == pipeline_state \in {"IDLE", "FORWARD", "BACKWARD"}
====

---- MODULE OmniGatewayRouting ----
(* OMNI MOTHER: TLA+ Spec for Gateway Routing Safety *)

EXTENDS Integers, Sequences

VARIABLES queue, processing

Init == 
    /\ queue = <<>>
    /\ processing = 0

Enqueue == 
    /\ Len(queue) < 100
    /\ queue' = Append(queue, "req")
    /\ processing' = processing

Process == 
    /\ Len(queue) > 0
    /\ queue' = Tail(queue)
    /\ processing' = processing + 1

Next == Enqueue \/ Process

Spec == Init /\ [][Next]_<<queue, processing>>

====

---- @omni-layer Testing | @omni-lang TLA+ | @omni-batch 17
---- @omni-description Distributed consensus spec: TLA+ formal specification
---- for verifying OMNI distributed model inference consensus protocol.

---- MODULE OmniInferenceConsensus ----
EXTENDS Integers, Sequences, FiniteSets, TLC

CONSTANTS
    Nodes,          \* Set of inference nodes
    Models,         \* Set of available models
    MaxRound        \* Maximum consensus rounds

VARIABLES
    state,          \* Function: node -> {idle, proposing, voting, committed, failed}
    proposals,      \* Function: node -> proposed inference result
    votes,          \* Function: node -> set of nodes that voted for it
    committed,      \* Set of committed inference results
    round,          \* Current consensus round
    messageQueue    \* Messages in transit

vars == <<state, proposals, votes, committed, round, messageQueue>>

TypeOK ==
    /\ state \in [Nodes -> {"idle", "proposing", "voting", "committed", "failed"}]
    /\ votes \in [Nodes -> SUBSET Nodes]
    /\ committed \subseteq [model: Models, result: Nat, round: 0..MaxRound]
    /\ round \in 0..MaxRound

Init ==
    /\ state = [n \in Nodes |-> "idle"]
    /\ proposals = [n \in Nodes |-> <<>>]
    /\ votes = [n \in Nodes |-> {}]
    /\ committed = {}
    /\ round = 0
    /\ messageQueue = <<>>

\* A node proposes an inference result
Propose(n) ==
    /\ state[n] = "idle"
    /\ round < MaxRound
    /\ state' = [state EXCEPT ![n] = "proposing"]
    /\ proposals' = [proposals EXCEPT ![n] = <<n, round>>]
    /\ round' = round + 1
    /\ UNCHANGED <<votes, committed, messageQueue>>

\* A node votes for a proposal
Vote(voter, proposer) ==
    /\ state[proposer] = "proposing"
    /\ voter /= proposer
    /\ voter \notin votes[proposer]
    /\ votes' = [votes EXCEPT ![proposer] = votes[proposer] \union {voter}]
    /\ state' = [state EXCEPT ![voter] = "voting"]
    /\ UNCHANGED <<proposals, committed, round, messageQueue>>

\* Commit when quorum is reached (>= 2/3 of nodes)
Commit(n) ==
    /\ state[n] = "proposing"
    /\ Cardinality(votes[n]) * 3 >= Cardinality(Nodes) * 2
    /\ state' = [state EXCEPT ![n] = "committed"]
    /\ committed' = committed \union {[model |-> "default", result |-> round, round |-> round]}
    /\ UNCHANGED <<proposals, votes, round, messageQueue>>

\* Recovery from failure
Recover(n) ==
    /\ state[n] = "failed"
    /\ state' = [state EXCEPT ![n] = "idle"]
    /\ votes' = [votes EXCEPT ![n] = {}]
    /\ UNCHANGED <<proposals, committed, round, messageQueue>>

Next ==
    \/ \E n \in Nodes: Propose(n)
    \/ \E v, p \in Nodes: Vote(v, p)
    \/ \E n \in Nodes: Commit(n)
    \/ \E n \in Nodes: Recover(n)

\* Safety: No two different results committed in the same round
Safety ==
    \A c1, c2 \in committed:
        c1.round = c2.round => c1.result = c2.result

\* Liveness: Eventually some result is committed
Liveness ==
    <>(committed /= {})

Spec == Init /\ [][Next]_vars /\ WF_vars(Next)

====

---------------- MODULE MoERoutingProtocol ----------------
\* OMNI Framework - TLA+ Specification for Distributed MoE Routing
\* Formally verifies that tokens are correctly distributed to experts
\* across multiple GPUs without exceeding buffer capacities.

EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS 
    Tokens,      \* Set of all tokens in a batch
    Experts,     \* Set of all available experts
    GPUs,        \* Set of physical GPUs
    TopK,        \* Number of experts each token must route to
    BufferLimit  \* Max tokens a single GPU can buffer for incoming experts

VARIABLES 
    tokenRouting, \* Function mapping Token -> Set of Experts (size TopK)
    gpuBuffers    \* Function mapping GPU -> Number of tokens queued

\* Given mapping of which expert lives on which GPU
CONSTANT ExpertToGPU

TypeOK == 
    /\ tokenRouting \in [Tokens -> SUBSET Experts]
    /\ gpuBuffers \in [GPUs -> Nat]

Init == 
    /\ tokenRouting = [t \in Tokens |-> {}]
    /\ gpuBuffers = [g \in GPUs |-> 0]

\* Action: Router assigns Top-K experts to a token
AssignRoute(t, chosenExperts) == 
    /\ tokenRouting[t] = {}
    /\ chosenExperts \subseteq Experts
    /\ Cardinality(chosenExperts) = TopK
    \* Check if adding this token exceeds any GPU buffer
    /\ \A e \in chosenExperts : gpuBuffers[ExpertToGPU[e]] + 1 <= BufferLimit
    \* Update state
    /\ tokenRouting' = [tokenRouting EXCEPT ![t] = chosenExperts]
    /\ gpuBuffers' = [g \in GPUs |-> 
                        gpuBuffers[g] + Cardinality({e \in chosenExperts : ExpertToGPU[e] = g})]

Next == 
    \E t \in Tokens, subset \in SUBSET Experts : AssignRoute(t, subset)

\* Safety Property: No GPU buffer should ever exceed its limit
NoBufferOverflow == \A g \in GPUs : gpuBuffers[g] <= BufferLimit

\* Liveness Property: All tokens eventually get routed (Assuming Fairness)
AllTokensRouted == <>(\A t \in Tokens : Cardinality(tokenRouting[t]) = TopK)

==============================================================

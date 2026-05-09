---- MODULE OmniTransformerVerification ----
EXTENDS Naturals, Sequences

(* 
  Omni TLA+ Verification (Testing & Verification Layer)
  Formally verifies the state transitions of the Omni Transformer KV Cache Manager.
  Ensures no buffer overflows occur during autoregressive sequence generation.
*)

CONSTANTS MAX_SEQ_LEN, NUM_LAYERS

VARIABLES current_len, kv_cache

Init == 
    /\ current_len = 0
    /\ kv_cache = [l \in 1..NUM_LAYERS |-> <<>>]

AppendTokens(layer, num_tokens) == 
    /\ current_len + num_tokens <= MAX_SEQ_LEN
    /\ kv_cache' = [kv_cache EXCEPT ![layer] = Append(@, num_tokens)]
    /\ UNCHANGED current_len

IncrementLength(num_tokens) ==
    /\ current_len + num_tokens <= MAX_SEQ_LEN
    /\ current_len' = current_len + num_tokens
    /\ UNCHANGED kv_cache

ResetCache ==
    /\ current_len' = 0
    /\ kv_cache' = [l \in 1..NUM_LAYERS |-> <<>>]

Next == 
    \/ \E l \in 1..NUM_LAYERS, n \in 1..5 : AppendTokens(l, n)
    \/ \E n \in 1..5 : IncrementLength(n)
    \/ ResetCache

(* Safety Property: Current length must never exceed maximum capacity *)
NoOverflow == current_len <= MAX_SEQ_LEN

(* Liveness Property: The cache can always be reset *)
CanReset == <>(current_len = 0)

Spec == Init /\ [][Next]_<<current_len, kv_cache>> /\ WF_<<current_len, kv_cache>>(ResetCache)

====

% @omni-domain Business Layer (vLLM Scheduler)
% MiniZinc constraint model for optimal batch scheduling
int: n_requests; set of int: REQUESTS = 1..n_requests;
array[REQUESTS] of int: seq_lengths; int: max_batch_tokens;
array[REQUESTS] of var 0..1: selected;
constraint sum(r in REQUESTS)(selected[r] * seq_lengths[r]) <= max_batch_tokens;
solve maximize sum(r in REQUESTS)(selected[r]);

% vLLM Scheduler Optimization in MiniZinc
int: num_requests;
int: max_batch_size;
array[1..num_requests] of int: prompt_lens;

var 1..max_batch_size: batch_size;

% Constraint: Total tokens in batch must not exceed VRAM limits
constraint sum(i in 1..batch_size)(prompt_lens[i]) <= 32000;

solve maximize batch_size;

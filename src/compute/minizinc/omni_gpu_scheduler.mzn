% OMNI Constraint Layer — MiniZinc GPU Scheduling Optimizer
% Optimal batch scheduling for transformer inference workloads.

include "globals.mzn";

% Parameters
int: num_requests;
int: num_gpus;
int: max_batch_size;
int: time_horizon;

set of int: REQUESTS = 1..num_requests;
set of int: GPUS = 1..num_gpus;
set of int: TIME_SLOTS = 1..time_horizon;

array[REQUESTS] of int: request_tokens;    % Token count per request
array[REQUESTS] of int: request_priority;  % Priority (higher = more important)
array[REQUESTS] of int: request_deadline;  % Deadline time slot
array[GPUS] of int: gpu_memory_mb;         % Available VRAM per GPU
int: tokens_per_mb = 100;                   % Approximate tokens per MB

% Decision variables
array[REQUESTS] of var GPUS: gpu_assignment;      % Which GPU for each request
array[REQUESTS] of var TIME_SLOTS: start_time;     % When to start each request
array[REQUESTS] of var 1..max_batch_size: batch_id; % Batch grouping

% Constraints
% 1. Each GPU can handle at most max_batch_size concurrent requests per time slot
constraint forall(g in GPUS, t in TIME_SLOTS)(
    sum(r in REQUESTS where gpu_assignment[r] = g /\ start_time[r] = t)(1) <= max_batch_size
);

% 2. GPU memory constraint: total tokens on a GPU at any time <= memory capacity
constraint forall(g in GPUS, t in TIME_SLOTS)(
    sum(r in REQUESTS where gpu_assignment[r] = g /\ start_time[r] = t)(request_tokens[r])
    <= gpu_memory_mb[g] * tokens_per_mb
);

% 3. Meet deadlines
constraint forall(r in REQUESTS)(
    start_time[r] <= request_deadline[r]
);

% 4. Requests in same batch must be on same GPU and same time
constraint forall(r1, r2 in REQUESTS where r1 < r2)(
    (batch_id[r1] = batch_id[r2]) -> (gpu_assignment[r1] = gpu_assignment[r2] /\ start_time[r1] = start_time[r2])
);

% Objective: Minimize weighted latency + maximize throughput
var int: total_latency = sum(r in REQUESTS)(start_time[r] * request_priority[r]);
var int: gpu_utilization = sum(g in GPUS, t in TIME_SLOTS)(
    bool2int(exists(r in REQUESTS)(gpu_assignment[r] = g /\ start_time[r] = t))
);

solve minimize total_latency - gpu_utilization * 10;

output [
    "GPU assignments: ", show(gpu_assignment), "\n",
    "Start times: ", show(start_time), "\n",
    "Batch IDs: ", show(batch_id), "\n",
    "Total latency score: ", show(total_latency), "\n",
    "GPU utilization: ", show(gpu_utilization), "\n"
];

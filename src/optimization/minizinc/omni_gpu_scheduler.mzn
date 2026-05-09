% OMNI Optimization — GPU Scheduling Constraints
int: num_jobs;
int: num_gpus;

array[1..num_jobs] of int: job_memory_req;
array[1..num_gpus] of int: gpu_memory_cap;

% Decision variable: which GPU runs which job?
array[1..num_jobs] of var 1..num_gpus: assignment;

% Constraint: Total memory on each GPU cannot exceed its capacity
constraint forall(g in 1..num_gpus)(
    sum(j in 1..num_jobs where assignment[j] == g)(job_memory_req[j]) <= gpu_memory_cap[g]
);

% Objective: Minimize max memory usage across all GPUs for load balancing
var int: max_utilization = max(g in 1..num_gpus)(
    sum(j in 1..num_jobs where assignment[j] == g)(job_memory_req[j])
);

solve minimize max_utilization;

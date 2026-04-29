% Omni Resource Scheduler (MiniZinc)
% NP-Hard Constraint Optimization for GPU Workload Distribution

int: num_gpus;
int: num_tasks;

array[1..num_tasks] of int: task_memory;
array[1..num_gpus] of int: gpu_memory;

% Decision variables: which GPU runs which task
array[1..num_tasks] of var 1..num_gpus: assignment;

% Constraint: Total memory of tasks on a GPU cannot exceed its capacity
constraint forall(g in 1..num_gpus) (
    sum(t in 1..num_tasks where assignment[t] == g)(task_memory[t]) <= gpu_memory[g]
);

% Objective: Minimize the maximum memory used on any single GPU (Load balancing)
var int: max_mem_used = max(g in 1..num_gpus) (
    sum(t in 1..num_tasks where assignment[t] == g)(task_memory[t])
);

solve minimize max_mem_used;

output ["Assignments: ", show(assignment), "\nMax Mem Used: ", show(max_mem_used)];

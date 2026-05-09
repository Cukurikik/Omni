% OMNI Framework - MiniZinc Constraint Model for AthenaOS Task Allocation
% Allocates AI agent tasks to available compute nodes based on constraints.

int: num_tasks;
int: num_nodes;

set of int: TASKS = 1..num_tasks;
set of int: NODES = 1..num_nodes;

array[TASKS] of int: cpu_required;
array[TASKS] of int: mem_required;

array[NODES] of int: cpu_capacity;
array[NODES] of int: mem_capacity;

% Decision variable: which node is assigned to which task
array[TASKS] of var NODES: assignment;

% Constraint: Compute capacity cannot be exceeded
constraint forall(n in NODES) (
    sum(t in TASKS where assignment[t] == n)(cpu_required[t]) <= cpu_capacity[n]
);

% Constraint: Memory capacity cannot be exceeded
constraint forall(n in NODES) (
    sum(t in TASKS where assignment[t] == n)(mem_required[t]) <= mem_capacity[n]
);

% Objective: Load balancing - minimize the maximum CPU load across all nodes
var int: max_cpu_load;
constraint forall(n in NODES) (
    sum(t in TASKS where assignment[t] == n)(cpu_required[t]) <= max_cpu_load
);

solve minimize max_cpu_load;

output [
    "Assignment: \(assignment)\n",
    "Max CPU Load: \(max_cpu_load)\n"
];

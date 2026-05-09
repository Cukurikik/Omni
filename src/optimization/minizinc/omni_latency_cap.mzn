% OMNI Cluster Optimization Model using MiniZinc
% Objective: Minimize overall latency while respecting node capacity constraints

int: NumTasks;
int: NumNodes;

set of int: TASKS = 1..NumTasks;
set of int: NODES = 1..NumNodes;

array[TASKS] of int: CPU_Req;
array[NODES] of int: CPU_Cap;
array[TASKS, NODES] of int: Latency_Cost;

% Decision variables: Which node gets which task
array[TASKS] of var NODES: Assignment;

% Constraint: Don't exceed CPU capacity on any node
constraint forall(n in NODES) (
    sum(t in TASKS where Assignment[t] == n)(CPU_Req[t]) <= CPU_Cap[n]
);

% Objective: Minimize total latency
var int: TotalLatency = sum(t in TASKS)(Latency_Cost[t, Assignment[t]]);

solve minimize TotalLatency;

output [
    "Total Latency: \(TotalLatency)\n",
    "Assignments: \(Assignment)\n"
];

% OMNI Optimization — Power Limit Constraint Model
% Calculates optimal node deactivation to stay under datacenter power caps

int: num_nodes;
int: power_cap;

array[1..num_nodes] of int: power_usage;
array[1..num_nodes] of int: compute_capacity;

% Variables: 1 if node is active, 0 if deactivated
array[1..num_nodes] of var 0..1: node_active;

% Constraint: Total power must not exceed power_cap
constraint sum(i in 1..num_nodes) (node_active[i] * power_usage[i]) <= power_cap;

% Objective: Maximize total available compute capacity
solve maximize sum(i in 1..num_nodes) (node_active[i] * compute_capacity[i]);

output [
  "Active Nodes: ", show(node_active), "\n",
  "Total Compute: ", show(sum(i in 1..num_nodes) (node_active[i] * compute_capacity[i])), "\n"
];

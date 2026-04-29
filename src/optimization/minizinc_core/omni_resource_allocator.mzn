// OmniResourceAllocator - OMNI Constraint & Optimization Layer
//
// MiniZinc model for strictly bounded NP-hard resource allocation.
// Solves GPU workload scheduling for MoE inference across clusters.

int: num_gpus;
int: num_experts;
int: max_memory_per_gpu;

set of int: GPUS = 1..num_gpus;
set of int: EXPERTS = 1..num_experts;

// Memory required by each expert
array[EXPERTS] of int: expert_memory;

// Decision Variable: which GPU hosts which expert
array[EXPERTS] of var GPUS: assignment;

// Constraint: Total memory on any GPU cannot exceed its max memory
constraint forall(g in GPUS)(
    sum(e in EXPERTS where assignment[e] == g)(expert_memory[e]) <= max_memory_per_gpu
);

// Objective: Load balance the memory as evenly as possible
// We minimize the maximum memory usage across all GPUs
var int: max_used_memory;

constraint forall(g in GPUS)(
    sum(e in EXPERTS where assignment[e] == g)(expert_memory[e]) <= max_used_memory
);

solve minimize max_used_memory;

output [
    "Assignment: \(assignment)\n",
    "Max GPU Memory Used: \(max_used_memory)\n"
];

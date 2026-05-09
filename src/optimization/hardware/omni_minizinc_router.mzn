% Omni Hardware Routing Optimizer (MiniZinc)
% Constraint & Optimization Layer
% Computes the optimal mapping of Transformer layers to available GPU nodes
% based on VRAM capacity, interconnect bandwidth, and processing speed.

int: num_layers;
int: num_gpus;

set of int: LAYERS = 1..num_layers;
set of int: GPUS = 1..num_gpus;

% Input parameters
array[LAYERS] of int: layer_vram_req;
array[LAYERS] of int: layer_compute_req;

array[GPUS] of int: gpu_vram_cap;
array[GPUS] of int: gpu_compute_cap;

% Bandwidth penalty if sequential layers are not on the same GPU
array[GPUS, GPUS] of int: interconnect_latency;

% Decision Variables: Which GPU executes which layer
array[LAYERS] of var GPUS: layer_mapping;

% Constraints
% 1. VRAM Capacity constraint per GPU
constraint forall(g in GPUS)(
    sum(l in LAYERS where layer_mapping[l] == g)(layer_vram_req[l]) <= gpu_vram_cap[g]
);

% 2. Compute Capacity constraint per GPU
constraint forall(g in GPUS)(
    sum(l in LAYERS where layer_mapping[l] == g)(layer_compute_req[l]) <= gpu_compute_cap[g]
);

% Objective: Minimize the total latency across all sequential layer handoffs
var int: total_latency = sum(l in 1..num_layers-1)(
    interconnect_latency[layer_mapping[l], layer_mapping[l+1]]
);

solve minimize total_latency;

output [
    "Optimal Layer Mapping: ", show(layer_mapping), "\n",
    "Total Interconnect Latency: ", show(total_latency)
];

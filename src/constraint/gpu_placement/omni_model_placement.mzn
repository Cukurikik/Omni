% @omni-layer Constraint | @omni-lang MiniZinc | @omni-batch 17
% @omni-description Model placement optimizer: constraint satisfaction for
% optimal GPU allocation of inference workloads across a cluster.

include "globals.mzn";

% Parameters
int: n_models;                         % Number of models to place
int: n_gpus;                           % Number of available GPUs
array[1..n_models] of int: model_vram; % VRAM requirement per model (MB)
array[1..n_models] of int: model_flops;% Compute requirement (GFLOPS)
array[1..n_models] of int: model_priority; % Priority (higher = more important)
array[1..n_gpus] of int: gpu_vram;     % Available VRAM per GPU (MB)
array[1..n_gpus] of int: gpu_flops;    % Available FLOPS per GPU

% Decision variables
array[1..n_models] of var 1..n_gpus: placement; % Which GPU each model goes to
array[1..n_models] of var 0..1: is_placed;       % Whether model is placed

% Constraints

% 1. VRAM capacity: total VRAM used on each GPU <= available
constraint forall(g in 1..n_gpus)(
    sum(m in 1..n_models where is_placed[m] = 1 /\ placement[m] = g)(model_vram[m])
    <= gpu_vram[g]
);

% 2. Compute capacity: total FLOPS on each GPU <= available
constraint forall(g in 1..n_gpus)(
    sum(m in 1..n_models where is_placed[m] = 1 /\ placement[m] = g)(model_flops[m])
    <= gpu_flops[g]
);

% 3. Load balancing: max utilization difference between GPUs <= 30%
var float: max_util;
var float: min_util;
constraint max_util = max(g in 1..n_gpus)(
    sum(m in 1..n_models where is_placed[m] = 1 /\ placement[m] = g)(model_vram[m]) / gpu_vram[g]
);
constraint min_util = min(g in 1..n_gpus)(
    sum(m in 1..n_models where is_placed[m] = 1 /\ placement[m] = g)(model_vram[m]) / gpu_vram[g]
);
constraint max_util - min_util <= 0.3;

% 4. Co-location preference: models with same priority on same GPU
constraint forall(m1, m2 in 1..n_models where m1 < m2)(
    if model_priority[m1] = model_priority[m2] /\ is_placed[m1] = 1 /\ is_placed[m2] = 1
    then placement[m1] = placement[m2]
    else true
    endif
);

% Objective: maximize total weighted placement value
var int: total_value;
constraint total_value = sum(m in 1..n_models)(
    is_placed[m] * model_priority[m] * model_flops[m]
);

solve maximize total_value;

% Output
output [
    "Placement:\n",
    "Total value: ", show(total_value), "\n"
] ++ [
    "Model " ++ show(m) ++ " -> GPU " ++ show(placement[m]) ++
    " (placed=" ++ show(is_placed[m]) ++ ")\n"
    | m in 1..n_models
];

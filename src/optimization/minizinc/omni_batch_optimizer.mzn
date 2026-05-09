% OMNI Framework - Batch Optimizer (MiniZinc)
% Optimization logic to determine the best batch size and gradient accumulation
% steps given VRAM constraints during LLM pretraining.

int: available_vram_gb;
int: model_memory_footprint_gb;
int: activation_memory_per_sample_mb;

% Decision variables
var 1..1024: batch_size;
var 1..32: gradient_accumulation_steps;

% Objective: Maximize effective batch size
var int: effective_batch = batch_size * gradient_accumulation_steps;

% Constraint: Total VRAM used by model + activations must not exceed available VRAM
constraint 
    model_memory_footprint_gb * 1024 + (batch_size * activation_memory_per_sample_mb) <= available_vram_gb * 1024;

solve maximize effective_batch;

output [
    "Optimal Batch Size: ", show(batch_size), "\n",
    "Gradient Accumulation Steps: ", show(gradient_accumulation_steps), "\n",
    "Effective Batch: ", show(effective_batch), "\n"
];

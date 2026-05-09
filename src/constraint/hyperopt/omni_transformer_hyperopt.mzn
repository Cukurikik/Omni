% @omni-layer Constraint | @omni-lang MiniZinc | @omni-batch 18 | @omni-semester 16
% @omni-description MiniZinc constraint model for optimal transformer
% hyperparameter selection: d_model, n_heads, n_layers, batch_size.

include "globals.mzn";

% Decision variables
var 128..2048: d_model;
var 1..32: n_heads;
var 1..48: n_layers;
var 1..128: batch_size;
var 64..4096: seq_len;

% Derived
var int: head_dim = d_model div n_heads;
var int: params_m = (12 * d_model * d_model * n_layers + d_model * 32000) div 1000000;
var int: flops_per_token = 2 * n_layers * (4 * d_model * d_model + 2 * seq_len * d_model);
var int: memory_mb = (params_m * 4) + (batch_size * seq_len * d_model * 4 div 1000000);

% Constraints
constraint d_model mod n_heads == 0;
constraint head_dim >= 16;
constraint head_dim <= 256;
constraint d_model mod 64 == 0;  % alignment

% Hardware constraints
constraint memory_mb <= 24000;  % 24GB GPU
constraint params_m <= 7000;    % 7B parameters max

% Performance constraints
constraint batch_size * seq_len <= 32768;  % max tokens per batch

% Quality constraints (heuristic)
constraint n_layers >= 2 * n_heads div 3;  % depth proportional to width
constraint d_model >= 4 * n_heads * 16;    % minimum capacity

% Objective: maximize model capacity within constraints
var int: capacity_score = d_model * n_layers * n_heads;

solve maximize capacity_score;

output [
  "Optimal Transformer Config:\n",
  "  d_model:    ", show(d_model), "\n",
  "  n_heads:    ", show(n_heads), "\n",
  "  head_dim:   ", show(head_dim), "\n",
  "  n_layers:   ", show(n_layers), "\n",
  "  batch_size: ", show(batch_size), "\n",
  "  seq_len:    ", show(seq_len), "\n",
  "  params_M:   ", show(params_m), "\n",
  "  memory_MB:  ", show(memory_mb), "\n",
  "  capacity:   ", show(capacity_score), "\n"
];

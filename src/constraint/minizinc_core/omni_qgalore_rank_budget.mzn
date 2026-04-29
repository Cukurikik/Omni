-- Omni Q-GaLore Rank Budget Constraint (MiniZinc)
-- Ref: VITA-Group/Q-GaLore — Apache-2.0
int: n_layers;
int: budget;
int: base_rank;
array[1..n_layers] of var 1..base_rank: ranks;
array[1..n_layers] of float: grad_norms;
constraint sum(ranks) <= budget;
constraint forall(i in 1..n_layers)(ranks[i] >= 1);
solve maximize sum(i in 1..n_layers)(ranks[i] * grad_norms[i]);

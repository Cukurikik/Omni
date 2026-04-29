% Omni ICL Exemplar Optimizer (MiniZinc)
% Ref: HKUNLP/icl-ceil — ICML 2023
int: n_candidates;
int: k_select;
array[1..n_candidates] of float: relevance;
array[1..n_candidates] of float: diversity;
array[1..n_candidates] of var 0..1: selected;
constraint sum(selected) = k_select;
var float: objective = sum(i in 1..n_candidates)(
  selected[i] * (0.6 * relevance[i] + 0.4 * diversity[i])
);
solve maximize objective;

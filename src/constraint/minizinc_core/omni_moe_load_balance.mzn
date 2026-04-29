// Omni MoE Constraint Optimizer (MiniZinc)
// Constraint Layer: Expert load balancing constraint solver.
// Ref: arpita8/Awesome-Mixture-of-Experts-Papers
int: n_experts;
int: n_tokens;
array[1..n_tokens] of var 1..n_experts: assignment;
array[1..n_experts] of var int: load;
constraint forall(e in 1..n_experts)(load[e] = sum(t in 1..n_tokens)(bool2int(assignment[t] = e)));
constraint forall(e in 1..n_experts)(load[e] >= n_tokens div n_experts - 1);
constraint forall(e in 1..n_experts)(load[e] <= n_tokens div n_experts + 1);
solve minimize max(load) - min(load);

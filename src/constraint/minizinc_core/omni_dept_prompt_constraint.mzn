-- Omni DePT Prompt Tuning Constraint (MiniZinc)
-- Ref: ShiZhengyan/DePT — ICLR 2024
int: prompt_len;
int: rank;
float: alpha;
constraint rank >= 1;
constraint rank <= prompt_len;
constraint alpha >= 0.0 /\ alpha <= 1.0;
var int: shared_params = rank;
var int: task_params = prompt_len - rank;
var float: total_params = shared_params + task_params;
solve minimize total_params;

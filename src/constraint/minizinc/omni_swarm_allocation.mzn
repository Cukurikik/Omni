% OMNI Constraint Logic: AthenaOS Swarm Agent Allocation
int: num_tasks;
int: num_agents;

array[1..num_tasks] of int: task_difficulty;
array[1..num_agents] of int: agent_capacity;

% Decision variable: Which agent takes which task?
array[1..num_tasks] of var 1..num_agents: assignment;

% Constraint: No agent exceeds their capacity
constraint forall(a in 1..num_agents) (
    sum(t in 1..num_tasks where assignment[t] == a) (task_difficulty[t]) <= agent_capacity[a]
);

% Objective: Minimize the maximum load on any agent (load balancing)
var int: max_load = max(a in 1..num_agents) (
    sum(t in 1..num_tasks where assignment[t] == a) (task_difficulty[t])
);

solve minimize max_load;

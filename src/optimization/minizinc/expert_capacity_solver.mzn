% OMNI Framework - Expert Capacity Solver (MiniZinc)
% Formulates a constraint satisfaction problem to route a batch of N requests
% to M experts such that no expert exceeds its memory bandwidth capacity,
% while maximizing the affinity (Top-K preference) of requests to experts.

int: num_requests;
int: num_experts;
int: max_capacity;

set of int: REQUESTS = 1..num_requests;
set of int: EXPERTS = 1..num_experts;

% The predicted affinity/probability of Request i wanting Expert j
array[REQUESTS, EXPERTS] of int: affinity_scores;

% Decision Variable: 1 if Request i is routed to Expert j, else 0
array[REQUESTS, EXPERTS] of var 0..1: routing;

% Constraint 1: Each request MUST be routed to exactly K experts (Top-K routing)
int: top_k = 2;
constraint forall(r in REQUESTS) (
    sum(e in EXPERTS) (routing[r, e]) == top_k
);

% Constraint 2: No expert can receive more requests than its capacity
constraint forall(e in EXPERTS) (
    sum(r in REQUESTS) (routing[r, e]) <= max_capacity
);

% Objective: Maximize the total affinity score of the chosen routings
var int: total_affinity = sum(r in REQUESTS, e in EXPERTS) (
    routing[r, e] * affinity_scores[r, e]
);

solve maximize total_affinity;

output [
    "Routing Matrix:\n",
    concat([ if e == 1 then "\n" else " " endif ++ show(routing[r, e]) | r in REQUESTS, e in EXPERTS ]),
    "\nTotal Affinity Achieved: ", show(total_affinity), "\n"
];

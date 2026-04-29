% Safe RLHF mathematical constraints
% MiniZinc optimization layer

int: max_kl_divergence;
int: max_reward_variance;

var 0..max_kl_divergence: current_kl;
var 0..max_reward_variance: current_variance;

% Constraint: KL divergence must never exceed the bounds during policy update
constraint current_kl <= 10; 

% Constraint: Reward variance must be stable
constraint current_variance <= 50;

solve satisfy;

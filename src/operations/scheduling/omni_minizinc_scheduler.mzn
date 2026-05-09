% OMNI Constraint & Optimization Layer
% MiniZinc model for scheduling multi-node GPU training jobs to minimize makespan.

int: num_jobs;
int: num_gpus;
int: max_time;

set of int: JOBS = 1..num_jobs;
set of int: GPUS = 1..num_gpus;
set of int: TIME = 0..max_time;

array[JOBS] of int: duration;
array[JOBS] of int: gpu_req;

% Decision variables: Start time for each job
array[JOBS] of var TIME: start_time;

% Objective: Minimize the completion time of the last job
var TIME: makespan = max([start_time[j] + duration[j] | j in JOBS]);

% Cumulative constraint: Total GPUs used at any time cannot exceed num_gpus
include "cumulative.mzn";
constraint cumulative(start_time, duration, gpu_req, num_gpus);

% Ensure jobs finish within max_time
constraint forall(j in JOBS) (
    start_time[j] + duration[j] <= max_time
);

solve minimize makespan;

output [
    "Makespan: \(makespan)\n",
    "Schedule:\n"
] ++ [
    "Job \(j): Start=\(start_time[j]), End=\(start_time[j] + duration[j])\n" | j in JOBS
];

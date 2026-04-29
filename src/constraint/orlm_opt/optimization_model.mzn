int: num_tasks;
array[1..num_tasks] of var 1..num_tasks: task_assignment;
include "alldifferent.mzn";
constraint alldifferent(task_assignment);
solve satisfy;

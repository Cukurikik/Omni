% OMNI Constraint Layer: MiniZinc Model
int: n;
array[1..n] of var 1..n: q;
include "alldifferent.mzn";
constraint alldifferent(q);
solve satisfy;

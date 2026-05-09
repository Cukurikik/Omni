(* OMNI Framework - Wolfram Language Script for Symbolic Grokking Dynamics *)
(* Derives closed-form behavior or performs symbolic integration of learning equations *)

Print["OMNI Wolfram: Initializing symbolic analysis for Grokking Dynamics..."]

(* Define differential equations for Training Loss (L) and Weight Norm (W) *)
eq1 = L'[t] == -lr * L[t] * (1 + W[t]);
eq2 = W'[t] == lr * L[t] - wd * W[t];

(* Attempt to find a symbolic solution using DSolve *)
Print["OMNI Wolfram: Attempting to solve ODE system..."]
sol = DSolve[{eq1, eq2, L[0] == 2.0, W[0] == 0.1}, {L[t], W[t]}, t];

(* Output the derived formula, if a closed form exists. 
   Usually, coupled non-linear ODEs might not have simple closed forms, 
   so we analyze asymptotic behavior. *)
If[sol =!= {},
    Print["OMNI Wolfram: Closed-form solution found: ", sol],
    Print["OMNI Wolfram: No simple closed-form exists. Proceeding with Series expansion around t=0..."];
    
    (* Series expansion for early training dynamics *)
    L_approx = Series[L[t] /. {L'[t] -> -lr*L[t]*(1+W[t]), W'[t] -> lr*L[t]-wd*W[t], L[0]->2.0, W[0]->0.1}, {t, 0, 2}];
    Print["Taylor Expansion of Training Loss: ", L_approx];
]

(* OMNI Mathematica Package for Symbolic Tensor Manipulation *)

BeginPackage["OmniFramework`SymbolicCompute`"]

OptimizeTensorExpression::usage = "OptimizeTensorExpression[expr] applies symbolic simplifications to OMNI tensor graphs."

Begin["`Private`"]

OptimizeTensorExpression[expr_] := Module[{simplified},
  (* Apply algebraic simplification rules *)
  simplified = FullSimplify[expr];
  
  (* specific tensor optimizations: tr(A) + tr(B) -> tr(A+B) *)
  simplified = simplified /. {
    Tr[A_] + Tr[B_] :> Tr[A + B],
    Tr[A_]*c_ :> Tr[c*A]
  };
  
  Return[simplified];
]

End[]
EndPackage[]

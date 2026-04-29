// Omni LLM4Regression Analyzer (F#)
// Business Layer: Functional regression metric computation.
// Ref: robertvacareanu/llm4regression

module Omni.Llm4Regression

type RegressionResult = | Ok of float | Err of string

let computeMSE (preds: float list) (targets: float list) =
    if List.length preds <> List.length targets || List.isEmpty preds then Err "Mismatched"
    else
        let mse = List.map2 (fun p t -> (p - t) ** 2.0) preds targets |> List.average
        Ok (System.Math.Round(mse, 10))

// Omni Tool Retrieval Web (ReScript)
// Interface Layer: Type-safe functional UI logic compiled to JS.

type evalResult =
  | Success(float)
  | Error(string)

let evaluateToolRetrieval = (recallK: float): evalResult => {
  if (recallK < 0.0 || recallK > 1.0) {
    Error("Recall metric must be bounded between 0.0 and 1.0")
  } else {
    Success(recallK *. 100.0)
  }
}

let renderResult = (res: evalResult): string => {
  switch res {
  | Success(score) => "Retrieval Accuracy: " ++ Js.Float.toString(score) ++ "%"
  | Error(msg) => "EVAL_FAIL: " ++ msg
  }
}

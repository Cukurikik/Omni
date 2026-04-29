(* Prompt4ReasoningPapers — Chain-of-Thought Reasoning Analyzer (OCaml) *)
type ('a, 'e) omni_result = Ok of 'a | Err of 'e

type reasoning_step = { step_id: int; content: string; step_type: string }

let max_steps = 100
let max_content = 50000

let validate_chain (steps: reasoning_step list) : (int, string) omni_result =
  if steps = [] then Err "Empty reasoning chain"
  else if List.length steps > max_steps then Err "Steps exceed 100"
  else
    let valid = List.for_all (fun s ->
      String.length s.content <= max_content &&
      s.step_id >= 0 &&
      List.mem s.step_type ["premise"; "inference"; "conclusion"]
    ) steps in
    if valid then Ok (List.length steps) else Err "Invalid step found"

let compute_chain_accuracy (predicted: string list) (ground_truth: string list) : (float, string) omni_result =
  if predicted = [] then Err "Empty predicted"
  else if ground_truth = [] then Err "Empty ground truth"
  else
    let correct = List.length (List.filter (fun p -> List.mem p ground_truth) predicted) in
    Ok (float_of_int correct /. float_of_int (List.length ground_truth))

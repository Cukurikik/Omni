(* LLMSurvey — Model Benchmark Comparator (OCaml) *)
type ('a, 'e) omni_result = Ok of 'a | Err of 'e

type benchmark_entry = { model_name: string; task: string; score: float; params_b: float }

let max_entries = 10000

let rank_models (entries: benchmark_entry list) (task: string) : (benchmark_entry list, string) omni_result =
  if entries = [] then Err "Empty entries"
  else if List.length entries > max_entries then Err "Entries exceed limit"
  else
    let filtered = List.filter (fun e -> e.task = task) entries in
    if filtered = [] then Err ("No entries for task: " ^ task)
    else Ok (List.sort (fun a b -> compare b.score a.score) filtered)

let compute_efficiency_score (score: float) (params_b: float) : (float, string) omni_result =
  if score < 0.0 || score > 1.0 then Err "Score must be in [0,1]"
  else if params_b <= 0.0 then Err "Params must be positive"
  else Ok (score /. (log (params_b +. 1.0)))

(* Efficient LLMs Survey — Model Comparison Engine *)
(* OCaml pure functional model benchmark scorer *)

type omni_result = Ok of float | Err of string

let max_models = 10000

let compute_efficiency_score latency_ms throughput_tps params_b accuracy =
  if latency_ms <= 0.0 then Err "Latency must be positive"
  else if throughput_tps <= 0.0 then Err "Throughput must be positive"
  else if params_b <= 0.0 then Err "Parameters must be positive"
  else if accuracy < 0.0 || accuracy > 1.0 then Err "Accuracy must be in [0,1]"
  else
    let speed_score = throughput_tps /. latency_ms in
    let param_efficiency = accuracy /. (log (params_b +. 1.0)) in
    let composite = (0.4 *. speed_score) +. (0.6 *. param_efficiency) in
    Ok composite

let compare_models models =
  if List.length models > max_models then Err "Exceeds model limit"
  else
    let scored = List.map (fun (name, lat, thr, par, acc) ->
      (name, compute_efficiency_score lat thr par acc)) models in
    Ok (List.length scored |> float_of_int)

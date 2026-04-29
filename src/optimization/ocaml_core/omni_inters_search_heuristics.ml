(* Omni INTERS Search Heuristics (OCaml) *)
(* Pure functional optimization layer for search instruction tuning. *)

type search_result = { doc_id : int; relevance : float }
type result_t = Ok of search_result list | Error of string

let apply_instruction_heuristic (results : search_result list) (boost_factor : float) : result_t =
  if boost_factor < 0.0 then
    Error "Boost factor must be non-negative"
  else
    let boosted = List.map (fun r -> { r with relevance = r.relevance *. boost_factor }) results in
    let sorted = List.sort (fun a b -> compare b.relevance a.relevance) boosted in
    Ok sorted

let execute_tuning () =
  let initial = [{doc_id=1; relevance=0.5}; {doc_id=2; relevance=0.8}] in
  match apply_instruction_heuristic initial 1.5 with
  | Ok res -> res
  | Error _ -> []

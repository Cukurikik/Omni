(* Omni Lion Adversarial Distillation Verifier (OCaml) *)
(* Ref: YJiangcm/Lion — EMNLP 2023 *)

type distillation_step = { student_acc : float; teacher_acc : float; iteration : int }

let kl_divergence (p : float list) (q : float list) : float =
  List.fold_left2 (fun acc pi qi ->
    if pi > 1e-12 && qi > 1e-12 then acc +. pi *. log (pi /. qi) else acc
  ) 0.0 p q

let discriminate_hard (student : float list) (teacher : float list) (threshold : float) : int list =
  List.mapi (fun i (s, t) -> if t -. s > threshold then Some i else None)
    (List.combine student teacher)
  |> List.filter_map Fun.id

let improvement_trend (steps : distillation_step list) : float =
  match steps with
  | [] -> 0.0
  | [s] -> 0.0
  | first :: _ ->
    let last = List.nth steps (List.length steps - 1) in
    last.student_acc -. first.student_acc

(* Omni AlphaRec Graph Conv (OCaml) *)
(* Ref: LehengTHU/AlphaRec — ICLR 2025 *)
let dot a b = List.fold_left2 (fun acc x y -> acc +. x *. y) 0.0 a b
let graph_conv node neighbors self_w =
  let d = List.length node in
  if neighbors = [] then node
  else
    let n = float_of_int (List.length neighbors) in
    let agg = List.init d (fun i ->
      List.fold_left (fun s nb -> s +. List.nth nb i) 0.0 neighbors /. n) in
    List.map2 (fun ni ai -> self_w *. ni +. (1.0 -. self_w) *. ai) node agg

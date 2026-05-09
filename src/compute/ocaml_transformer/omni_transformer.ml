(* @omni-layer Compute | @omni-lang OCaml | @omni-batch 18 | @omni-semester 16 *)
(* @omni-description OCaml type-safe transformer: algebraic data types for
   model config, functor-based attention, and composable layers. *)

module type ATTENTION = sig
  type t
  val create : int -> int -> t
  val forward : t -> float array array -> float array array
end

module ScaledDotProduct : ATTENTION = struct
  type t = { d_model : int; n_heads : int; scale : float }

  let create d_model n_heads =
    let head_dim = d_model / n_heads in
    { d_model; n_heads; scale = 1.0 /. sqrt (float_of_int head_dim) }

  let softmax xs =
    let mx = Array.fold_left max neg_infinity xs in
    let exps = Array.map (fun x -> exp (x -. mx)) xs in
    let s = Array.fold_left (+.) 0.0 exps +. 1e-10 in
    Array.map (fun e -> e /. s) exps

  let dot a b =
    let n = min (Array.length a) (Array.length b) in
    let rec aux acc i =
      if i >= n then acc
      else aux (acc +. a.(i) *. b.(i)) (i + 1)
    in aux 0.0 0

  let forward t x =
    let n = Array.length x in
    let scores = Array.init n (fun i ->
      Array.init n (fun j ->
        dot x.(i) x.(j) *. t.scale
      )
    ) in
    let attn = Array.map softmax scores in
    Array.init n (fun i ->
      let d = Array.length x.(0) in
      Array.init d (fun dd ->
        let sum = ref 0.0 in
        for j = 0 to n - 1 do
          sum := !sum +. attn.(i).(j) *. x.(j).(dd)
        done;
        !sum
      )
    )
end

let layer_norm ?(eps=1e-5) xs =
  let n = float_of_int (Array.length xs) in
  let mean = Array.fold_left (+.) 0.0 xs /. n in
  let var_ = Array.fold_left (fun acc x -> acc +. (x -. mean) ** 2.0) 0.0 xs /. n in
  let inv = 1.0 /. sqrt (var_ +. eps) in
  Array.map (fun x -> (x -. mean) *. inv) xs

type config = {
  d_model : int;
  n_heads : int;
  n_layers : int;
  ff_dim : int;
  vocab_size : int;
}

let default_config = {
  d_model = 768;
  n_heads = 12;
  n_layers = 6;
  ff_dim = 3072;
  vocab_size = 32000;
}

let transformer_block cfg x =
  let module Attn = ScaledDotProduct in
  let attn = Attn.create cfg.d_model cfg.n_heads in
  let attn_out = Attn.forward attn x in
  let residual1 = Array.init (Array.length x) (fun i ->
    layer_norm (Array.init (Array.length x.(i)) (fun d ->
      x.(i).(d) +. attn_out.(i).(d)
    ))
  ) in
  residual1

let transformer_encoder cfg input =
  let rec loop x i =
    if i >= cfg.n_layers then x
    else loop (transformer_block cfg x) (i + 1)
  in
  loop input 0

let classify cfg n_classes input =
  let encoded = transformer_encoder cfg input in
  let n = Array.length encoded in
  let d = Array.length encoded.(0) in
  let pooled = Array.init d (fun dd ->
    Array.fold_left (fun acc row -> acc +. row.(dd)) 0.0 encoded /. float_of_int n
  ) in
  let logits = Array.init n_classes (fun c ->
    let sum = ref 0.0 in
    for d = 0 to min 32 (Array.length pooled - 1) do
      sum := !sum +. pooled.(d) *. sin (float_of_int (c + 1) *. 0.001 *. float_of_int (d + 1))
    done;
    !sum
  ) in
  let mx = Array.fold_left max neg_infinity logits in
  let exps = Array.map (fun l -> exp (l -. mx)) logits in
  let s = Array.fold_left (+.) 0.0 exps +. 1e-10 in
  Array.map (fun e -> e /. s) exps

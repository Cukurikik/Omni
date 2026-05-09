(* OMNI Compute — OCaml Type-Safe Tensor Operations *)
(* Strongly typed tensor algebra for verified compute kernels. *)

module Tensor = struct
  type shape = int list

  type t = {
    data : float array;
    shape : shape;
    strides : int list;
  }

  let numel shape = List.fold_left ( * ) 1 shape

  let compute_strides shape =
    let rec aux acc = function
      | [] -> List.rev acc
      | _ :: rest ->
        let stride = List.fold_left ( * ) 1 rest in
        aux (stride :: acc) rest
    in
    aux [] shape

  let create shape init_val =
    let n = numel shape in
    { data = Array.make n init_val; shape; strides = compute_strides shape }

  let zeros shape = create shape 0.0
  let ones shape = create shape 1.0

  let get t indices =
    let idx = List.fold_left2 (fun acc i s -> acc + i * s) 0 indices t.strides in
    t.data.(idx)

  let set t indices value =
    let idx = List.fold_left2 (fun acc i s -> acc + i * s) 0 indices t.strides in
    t.data.(idx) <- value

  let map f t =
    { t with data = Array.map f t.data }

  let map2 f a b =
    assert (a.shape = b.shape);
    { a with data = Array.init (Array.length a.data) (fun i -> f a.data.(i) b.data.(i)) }

  let add = map2 ( +. )
  let sub = map2 ( -. )
  let mul = map2 ( *. )

  let dot a b =
    assert (a.shape = b.shape);
    let sum = ref 0.0 in
    Array.iteri (fun i v -> sum := !sum +. v *. b.data.(i)) a.data;
    !sum

  let matmul a b =
    match a.shape, b.shape with
    | [m; k1], [k2; n] when k1 = k2 ->
      let result = zeros [m; n] in
      for i = 0 to m - 1 do
        for j = 0 to n - 1 do
          let s = ref 0.0 in
          for p = 0 to k1 - 1 do
            s := !s +. (get a [i; p]) *. (get b [p; j])
          done;
          set result [i; j] !s
        done
      done;
      result
    | _ -> failwith "matmul: incompatible shapes"

  let softmax t =
    let max_val = Array.fold_left max neg_infinity t.data in
    let exps = Array.map (fun x -> exp (x -. max_val)) t.data in
    let sum = Array.fold_left ( +. ) 0.0 exps in
    { t with data = Array.map (fun x -> x /. sum) exps }

  let layer_norm t gamma beta eps =
    let n = float_of_int (Array.length t.data) in
    let mean = Array.fold_left ( +. ) 0.0 t.data /. n in
    let var_ =
      Array.fold_left (fun acc x -> acc +. (x -. mean) ** 2.0) 0.0 t.data /. n
    in
    let inv_std = 1.0 /. sqrt (var_ +. eps) in
    { t with data =
        Array.init (Array.length t.data) (fun i ->
          gamma.data.(i) *. (t.data.(i) -. mean) *. inv_std +. beta.data.(i))
    }

  let reshape t new_shape =
    assert (numel t.shape = numel new_shape);
    { t with shape = new_shape; strides = compute_strides new_shape }

  let to_string t =
    Printf.sprintf "Tensor(shape=[%s], numel=%d)"
      (String.concat "," (List.map string_of_int t.shape))
      (numel t.shape)
end

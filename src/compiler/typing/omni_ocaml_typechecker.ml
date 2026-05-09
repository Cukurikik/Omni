(* Omni Typechecker (OCaml) *)
(* Compiler & Metaprogramming Layer *)
(* Implements a Hindley-Milner style type checking pass for validating *)
(* the configuration topologies in Omnifile.toml and GraphQL schemas. *)

type omni_type =
  | TInt
  | TFloat
  | TString
  | TBool
  | TTensor of int list * omni_type  (* e.g., Tensor([1024, 1024], TFloat) *)
  | TFunction of omni_type * omni_type

type expr =
  | EInt of int
  | EFloat of float
  | EString of string
  | ETensor of int list * expr list
  | EApply of expr * expr

exception TypeError of string

let rec infer_type env e =
  match e with
  | EInt _ -> TInt
  | EFloat _ -> TFloat
  | EString _ -> TString
  | ETensor (shape, elements) ->
      if List.length elements = 0 then
        TTensor (shape, TFloat) (* Default to float for empty tensors *)
      else
        let t_elem = infer_type env (List.hd elements) in
        (* Verify all elements have the same type *)
        List.iter (fun elem ->
          let t = infer_type env elem in
          if t <> t_elem then raise (TypeError "Tensor elements type mismatch")
        ) elements;
        TTensor (shape, t_elem)
        
  | EApply (func, arg) ->
      let t_func = infer_type env func in
      let t_arg = infer_type env arg in
      match t_func with
      | TFunction (t_in, t_out) ->
          if t_in = t_arg then t_out
          else raise (TypeError "Function argument type mismatch")
      | _ -> raise (TypeError "Application of non-function")

let check_config expression =
  try
    let t = infer_type [] expression in
    Printf.printf "Typecheck passed!\n";
    t
  with
  | TypeError msg ->
      Printf.printf "Typecheck failed: %s\n" msg;
      exit 1

(* OMNI Compiler Layer *)
(* OCaml Implementation of the Universal Abstract Syntax Tree (UAST) Type Checker *)

type omni_type =
  | TInt
  | TFloat
  | TTensor of int list * omni_type (* e.g., Tensor([1, 64, 64], Float) *)
  | TArrow of omni_type * omni_type (* Function type: A -> B *)

type uast_node =
  | ConstInt of int
  | ConstFloat of float
  | TensorAlloc of int list * omni_type
  | Apply of uast_node * uast_node
  | Var of string

type type_env = (string * omni_type) list

exception TypeError of string

(* Type inference algorithm traversing the UAST *)
let rec type_check (env : type_env) (node : uast_node) : omni_type =
  match node with
  | ConstInt _ -> TInt
  | ConstFloat _ -> TFloat
  
  | TensorAlloc (dims, dtype) -> 
      TTensor (dims, dtype)
      
  | Var name ->
      (try List.assoc name env
       with Not_found -> raise (TypeError ("Unbound variable: " ^ name)))
       
  | Apply (fn_node, arg_node) ->
      let fn_type = type_check env fn_node in
      let arg_type = type_check env arg_node in
      match fn_type with
      | TArrow (t_in, t_out) ->
          if t_in = arg_type then t_out
          else raise (TypeError "Argument type mismatch in application")
      | _ -> raise (TypeError "Attempted to apply a non-function")

(* Helper function for testing *)
let string_of_type = function
  | TInt -> "int"
  | TFloat -> "float"
  | TTensor (dims, dtype) -> "tensor"
  | TArrow _ -> "function"

let () =
  let env = [("matmul", TArrow (TTensor ([16; 16], TFloat), TTensor ([16; 16], TFloat)))] in
  let tensor_a = TensorAlloc ([16; 16], TFloat) in
  let ast = Apply (Var "matmul", tensor_a) in
  try
    let t = type_check env ast in
    Printf.printf "OMNI OCaml Compiler: Type check passed. Result type: %s\n" (string_of_type t)
  with TypeError msg ->
    Printf.printf "OMNI OCaml Compiler Error: %s\n" msg

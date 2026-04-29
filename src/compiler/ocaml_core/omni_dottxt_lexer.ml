(* Omni Dottxt Lexer (OCaml) *)
(* Compiler Layer: Strict deterministic lexical analysis for structured prompts. *)

type token =
  | LBRACE
  | RBRACE
  | IDENT of string
  | STRING of string
  | EOF

let is_alpha c =
  (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c = '_'

let tokenize input_str =
  let len = String.length input_str in
  let rec aux pos acc =
    if pos >= len then List.rev (EOF :: acc)
    else match input_str.[pos] with
      | ' ' | '\n' | '\t' -> aux (pos + 1) acc
      | '{' -> aux (pos + 1) (LBRACE :: acc)
      | '}' -> aux (pos + 1) (RBRACE :: acc)
      | c when is_alpha c ->
          let start = pos in
          let rec read_ident p =
            if p < len && is_alpha input_str.[p] then read_ident (p + 1) else p
          in
          let end_pos = read_ident pos in
          let ident_str = String.sub input_str start (end_pos - start) in
          aux end_pos (IDENT ident_str :: acc)
      | _ -> failwith "OMNI_ERR: Invalid character in prompt definition"
  in
  aux 0 []

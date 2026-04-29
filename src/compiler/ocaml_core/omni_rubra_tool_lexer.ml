(* Omni Rubra Tool Lexer (OCaml) *)
(* Compiler Layer: Lexical analysis for tool call JSON DSL. *)
(* Ref: rubra-ai/rubra *)
type token = LBRACE | RBRACE | COLON | COMMA | STRING of string | EOF
let tokenize input =
  let len = String.length input in
  let rec aux pos acc =
    if pos >= len then List.rev (EOF :: acc)
    else match input.[pos] with
      | '{' -> aux (pos+1) (LBRACE :: acc) | '}' -> aux (pos+1) (RBRACE :: acc)
      | ':' -> aux (pos+1) (COLON :: acc) | ',' -> aux (pos+1) (COMMA :: acc)
      | '"' -> let start = pos+1 in
               let rec rd p = if p < len && input.[p] <> '"' then rd (p+1) else p in
               let ep = rd start in aux (ep+1) (STRING (String.sub input start (ep-start)) :: acc)
      | ' ' | '\n' | '\t' -> aux (pos+1) acc
      | _ -> failwith "OMNI_ERR: Unexpected char"
  in aux 0 []

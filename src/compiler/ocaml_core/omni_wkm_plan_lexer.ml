(* Omni WKM Plan Lexer (OCaml) *)
(* Compiler Layer: Lexical analysis for world knowledge model plan DSL. *)
(* Ref: zjunlp/WKM *)

type token = GOAL of string | ACTION of string | ARROW | EOF

let tokenize input =
  let len = String.length input in
  let rec aux pos acc =
    if pos >= len then List.rev (EOF :: acc)
    else match input.[pos] with
      | ' ' | '\n' -> aux (pos + 1) acc
      | '-' when pos + 1 < len && input.[pos+1] = '>' -> aux (pos + 2) (ARROW :: acc)
      | c when c >= 'A' && c <= 'Z' ->
          let start = pos in
          let rec rd p = if p < len && input.[p] >= 'A' && input.[p] <= 'z' then rd (p+1) else p in
          let ep = rd pos in aux ep (GOAL (String.sub input start (ep-start)) :: acc)
      | c when c >= 'a' && c <= 'z' ->
          let start = pos in
          let rec rd p = if p < len && input.[p] >= 'a' && input.[p] <= 'z' then rd (p+1) else p in
          let ep = rd pos in aux ep (ACTION (String.sub input start (ep-start)) :: acc)
      | _ -> failwith "OMNI_ERR: Invalid char"
  in aux 0 []

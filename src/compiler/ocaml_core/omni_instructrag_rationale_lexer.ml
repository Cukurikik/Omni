(* Omni InstructRAG Rationale Lexer (OCaml) *)
(* Compiler Layer: Lexical analysis for rationale DSL. *)
(* Ref: weizhepei/InstructRAG — ICLR 2025 *)
type rationale_token = EVIDENCE | QUERY | RATIONALE | SEPARATOR | TEXT of string | EOF_R
let lex_rationale input =
  let parts = String.split_on_char '|' input in
  List.map (fun s ->
    let trimmed = String.trim s in
    if String.length trimmed = 0 then SEPARATOR
    else if String.sub trimmed 0 (min 3 (String.length trimmed)) = "Q:" then QUERY
    else if String.sub trimmed 0 (min 3 (String.length trimmed)) = "E:" then EVIDENCE
    else if String.sub trimmed 0 (min 3 (String.length trimmed)) = "R:" then RATIONALE
    else TEXT trimmed
  ) parts @ [EOF_R]

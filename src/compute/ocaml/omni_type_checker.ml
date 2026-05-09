module OmniTypeChecker = struct
  type omni_type = 
    | TInt
    | TFloat
    | TBool
    | TArrow of omni_type * omni_type

  type expression =
    | EInt of int
    | EFloat of float
    | EBool of bool
    | EAdd of expression * expression
    | EIf of expression * expression * expression

  exception TypeError of string

  let rec type_of env = function
    | EInt _ -> TInt
    | EFloat _ -> TFloat
    | EBool _ -> TBool
    | EAdd (e1, e2) ->
        let t1 = type_of env e1 in
        let t2 = type_of env e2 in
        if t1 = TInt && t2 = TInt then TInt
        else if t1 = TFloat && t2 = TFloat then TFloat
        else raise (TypeError "Type mismatch in Addition")
    | EIf (cond, e1, e2) ->
        if type_of env cond = TBool then
          let t1 = type_of env e1 in
          let t2 = type_of env e2 in
          if t1 = t2 then t1 else raise (TypeError "If branches mismatch")
        else raise (TypeError "Condition must be a boolean")
end

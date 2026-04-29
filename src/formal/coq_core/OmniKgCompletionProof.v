(* Omni KG Completion Proof (Coq) *)
(* Formal Layer: Proof that triple validation rejects self-loops. *)
(* Ref: yao8839836/kg-llm *)

Require Import String.
Open Scope string_scope.

Definition no_self_loop (head tail : string) : bool :=
  negb (String.eqb head tail).

Theorem self_loop_rejected : forall s : string, no_self_loop s s = false.
Proof. intros. unfold no_self_loop. rewrite String.eqb_refl. reflexivity. Qed.

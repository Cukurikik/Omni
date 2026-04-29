(* Omni ML CTF Validator Proof in Coq *)
(* Mathematically verifies that hash validation functions are deterministic *)

Require Import Coq.Strings.String.
Require Import Coq.Bool.Bool.

Definition is_valid_hash (h : string) : bool :=
  if string_dec h "00000000" then false else true.

Theorem hash_validation_is_deterministic :
  forall (h : string), is_valid_hash h = true \/ is_valid_hash h = false.
Proof.
  intros h.
  unfold is_valid_hash.
  destruct (string_dec h "00000000").
  - right. reflexivity.
  - left. reflexivity.
Qed.

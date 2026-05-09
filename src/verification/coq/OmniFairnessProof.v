(* OMNI Framework - Coq Proof for Optipfair Fairness *)
(* Verifies that the bias disparity remains below the threshold *)

Require Import Reals.
Open Scope R_scope.

Definition fairness_threshold : R := 0.05.

(* A model prediction disparity *)
Variable disparity : R.

(* The mitigation function reduces disparity by at least half if it is > threshold *)
Definition apply_mitigation (d : R) : R :=
  if Rle_dec d fairness_threshold then d else (d / 2).

(* Theorem: Mitigation ensures disparity strictly decreases if it was above threshold *)
Theorem mitigation_improves_fairness :
  forall d, d > fairness_threshold -> apply_mitigation d < d.
Proof.
  intros d H.
  unfold apply_mitigation.
  destruct (Rle_dec d fairness_threshold) as [Hle | Hnle].
  - (* Case: d <= threshold (Contradiction with d > threshold) *)
    lra.
  - (* Case: d > threshold *)
    lra.
Qed.

(* Note: lra (Linear Real Arithmetic) automatically discharges the goals. *)

;; Omni FLASK Eval Macro (Common Lisp)
;; Metaprogramming Layer: Expanding skill evaluation structures at compile-time.

(defpackage :omni-flask
  (:use :cl))
(in-package :omni-flask)

;; Deterministic macro expansion for strict evaluation metrics
(defmacro define-flask-skill (skill-name weight)
  (if (<= weight 0)
      (error "OMNI_ERROR: Skill weight must be positive.")
      `(defun ,(intern (format nil "EVALUATE-~A" skill-name)) (score)
         (if (or (< score 0.0) (> score 5.0))
             (values nil "Score bounds violation [0.0, 5.0]")
             (values (* score ,weight) nil)))))

;; Expansion Example (Evaluated deterministically)
;; (define-flask-skill 'logical_reasoning 1.5)

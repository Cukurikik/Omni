;; Omni User Model Validator (Lisp)
;; Rules Layer: LLM user modeling validation.
;; Ref: TamSiuhin/LLM-UM-Reading — User Modeling in LLM Era.
(defpackage :omni-um (:use :cl) (:export #:validate-profile))
(in-package :omni-um)
(defun validate-profile (profile)
  (and (listp profile)
       (assoc :user-id profile)
       (assoc :preferences profile)
       (> (length (cdr (assoc :preferences profile))) 0)))

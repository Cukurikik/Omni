;; Omni KG Completion Logic (Lisp)
;; Rules Layer: S-expression graph triple validation.
;; Ref: yao8839836/kg-llm

(defpackage :omni-kg (:use :cl) (:export #:validate-triple))
(in-package :omni-kg)

(defun validate-triple (head relation tail)
  (and (stringp head) (stringp relation) (stringp tail)
       (> (length head) 0) (> (length relation) 0) (> (length tail) 0)
       (not (string= head tail))))

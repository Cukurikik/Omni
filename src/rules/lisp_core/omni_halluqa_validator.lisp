;; Omni HalluQA Validator (Lisp)
;; Rules Layer: Hallucination QA validation rules.
;; Ref: OpenMOSS/HalluQA
(defpackage :omni-halluqa (:use :cl) (:export #:validate-answer))
(in-package :omni-halluqa)
(defun validate-answer (answer facts)
  (and (stringp answer)
       (> (length answer) 0)
       (listp facts)
       (> (length facts) 0)))

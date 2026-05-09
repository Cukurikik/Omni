;; OMNI Common Lisp Macro System for AST Transformation
(defpackage :omni-framework.compute
  (:use :cl))

(in-package :omni-framework.compute)

(defmacro define-omni-node (name &rest slots)
  "Generates a CLOS class and associated generic functions for an OMNI AST node."
  `(progn
     (defclass ,name ()
       ,(loop for slot in slots
              collect `(,slot :accessor ,slot :initarg ,(intern (symbol-name slot) "KEYWORD"))))
     (defmethod print-object ((node ,name) stream)
       (print-unreadable-object (node stream :type t :identity t)
         (format stream "OMNI-NODE: ~A" ',name)))))

;; Example Usage:
;; (define-omni-node tensor-op left-operand right-operand operation)

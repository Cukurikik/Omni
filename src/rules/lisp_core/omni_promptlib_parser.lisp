;; Omni Promptlib Parser (Common Lisp)
;; Rules Layer: S-expression based parsing for prompt structural validation.

(defpackage :omni-promptlib
  (:use :cl)
  (:export #:validate-prompt-structure))

(in-package :omni-promptlib)

(defun validate-prompt-structure (prompt-ast)
  "Validates that the prompt AST does not contain unescaped injection vectors."
  (cond
    ((null prompt-ast) t)
    ((atom prompt-ast)
     (if (and (stringp prompt-ast)
              (search "<script>" prompt-ast :test #'string-equal))
         nil
         t))
    (t (and (validate-prompt-structure (car prompt-ast))
            (validate-prompt-structure (cdr prompt-ast))))))

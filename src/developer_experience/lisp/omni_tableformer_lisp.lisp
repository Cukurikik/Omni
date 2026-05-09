;; OMNI Framework - Common Lisp Macro for TableFormer Data Grids
;; Facilitates metaprogramming to define tabular datasets cleanly for TableFormer models

(defpackage :omni-tableformer
  (:use :cl))

(in-package :omni-tableformer)

(defmacro define-omni-table (name headers &rest rows)
  "Macro to define a structured table dataset that compiles into a format ready for TableFormer serialization."
  `(defparameter ,name
     (list :headers ',headers
           :data (list ,@(loop for row in rows
                               collect `(list ,@row))))))

;; Example Usage:
;; (define-omni-table *financial-report*
;;   ("Year" "Revenue" "Profit")
;;   (2021 10000 2000)
;;   (2022 15000 3000)
;;   (2023 20000 4500))

(defun serialize-for-tableformer (table)
  "Serializes the defined table into a JSON-like representation for the Python backend."
  (format t "OMNI Serializing table with headers ~A~%" (getf table :headers))
  table)

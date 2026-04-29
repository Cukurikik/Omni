;; Omni BlenderLLM Metaprogramming Generator in Common Lisp
;; Generates strict CAD scripts via AST manipulation

(defpackage :omni-blender-cad
  (:use :cl)
  (:export :generate-cube-script))

(in-package :omni-blender-cad)

(defun generate-cube-script (size location-x location-y location-z)
  "Returns a Result-like alist indicating success or failure of Python bpy generation."
  (if (<= size 0)
      '((:success . nil) (:error . "Size must be strictly positive"))
      (let ((script (format nil "import bpy~%bpy.ops.mesh.primitive_cube_add(size=~A, location=(~A, ~A, ~A))" 
                            size location-x location-y location-z)))
        `((:success . t) (:script . ,script)))))

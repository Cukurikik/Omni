#lang racket
;; Omni ETO Macro (Racket)
;; Rules Layer: Macro for defining trajectory evaluation DSLs.
;; Ref: Yifan-Song793/ETO

(provide define-trajectory)

(define-syntax-rule (define-trajectory name (actions ...) (rewards ...))
  (define name
    (let ([a (list actions ...)] [r (list rewards ...)])
      (if (= (length a) (length r))
          (list 'trajectory a r)
          (error "OMNI_ERR: Action/reward mismatch")))))

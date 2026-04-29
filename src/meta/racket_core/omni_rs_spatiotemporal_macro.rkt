#lang racket
;; Omni RS SpatioTemporal Macro (Racket)
;; Metaprogramming Layer: Syntax extension for defining spatio-temporal layers.

(provide define-spatial-layer)

;; Deterministic macro to enforce bounds on layer instantiation
(define-syntax-rule (define-spatial-layer name x-dim y-dim t-dim)
  (begin
    (unless (and (> x-dim 0) (> y-dim 0) (> t-dim 0))
      (error 'define-spatial-layer "Dimensions must be strictly positive"))
    (define name (hash 'type "SpatialLayer" 
                       'dims (list x-dim y-dim t-dim)
                       'verified #t))))

;; Usage:
;; (define-spatial-layer Sentinel2 256 256 10)

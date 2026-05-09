#lang racket

;; OMNI Interface Layer: Domain Specific Language (DSL) in Racket
;; Defines hyper-parameters and network topologies elegantly using Lisp macros

(provide define-omni-network)

;; Syntax macro allowing a clean DSL for architecture definition
(define-syntax-rule (define-omni-network name
                      [layers ...]
                      [parameters ...])
  (define name
    (hash 'architecture '(layers ...)
          'hyperparams  (hash parameters ...))))

;; Usage of the DSL
(define-omni-network gpt-neo-omni
  ;; Layers topology definition
  [embedding-layer
   attention-block
   attention-block
   attention-block
   feedforward-projection
   lm-head]
  
  ;; Hyper-parameters mapping
  ['d-model 2048]
  ['heads 16]
  ['vocab-size 50257]
  ['dropout 0.1])

(define (export-network-config net)
  (displayln "OMNI Racket DSL: Exporting configuration...")
  (displayln (hash-ref net 'architecture))
  (displayln (hash-ref net 'hyperparams)))

(export-network-config gpt-neo-omni)

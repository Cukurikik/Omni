;; OMNI Metaprogramming — Scheme Symbolic Transformer DSL
;; S-expression based transformer architecture definition.

(define-record-type <layer-config>
  (make-layer-config name type params)
  layer-config?
  (name layer-name)
  (type layer-type)
  (params layer-params))

(define-record-type <model-spec>
  (make-model-spec name vocab-size embed-dim layers)
  model-spec?
  (name model-name)
  (vocab-size model-vocab)
  (embed-dim model-embed)
  (layers model-layers))

;; DSL for defining transformer architectures
(define (attention heads dim dropout)
  (make-layer-config "attention" 'multi-head-attention
    `((num-heads . ,heads) (head-dim . ,(/ dim heads)) (dropout . ,dropout))))

(define (feed-forward dim ffn-dim activation)
  (make-layer-config "ffn" 'feed-forward
    `((input-dim . ,dim) (hidden-dim . ,ffn-dim) (activation . ,activation))))

(define (layer-norm dim epsilon)
  (make-layer-config "norm" 'layer-norm
    `((dim . ,dim) (epsilon . ,epsilon))))

(define (transformer-block dim heads ffn-dim dropout)
  (list
    (layer-norm dim 1e-5)
    (attention heads dim dropout)
    (layer-norm dim 1e-5)
    (feed-forward dim ffn-dim 'gelu)))

(define (define-model name vocab embed num-layers heads ffn-dim dropout)
  (let ((blocks (apply append
          (map (lambda (_) (transformer-block embed heads ffn-dim dropout))
               (iota num-layers)))))
    (make-model-spec name vocab embed blocks)))

;; Compute parameter count
(define (count-parameters spec)
  (let* ((V (model-vocab spec))
         (D (model-embed spec))
         (L (length (model-layers spec)))
         (num-blocks (/ L 4))  ; 4 sub-layers per block
         (attn-params (* 4 D D))  ; Q,K,V,O projections
         (ffn-params (let* ((layers (model-layers spec))
                            (ffn (filter (lambda (l) (eq? (layer-type l) 'feed-forward)) layers)))
                       (if (null? ffn) (* 8 D D)
                           (let ((p (layer-params (car ffn))))
                             (+ (* (cdr (assq 'input-dim p)) (cdr (assq 'hidden-dim p)))
                                (* (cdr (assq 'hidden-dim p)) (cdr (assq 'input-dim p))))))))
         (embedding-params (* V D))
         (block-params (+ attn-params ffn-params (* 2 D))))
    (+ embedding-params (* num-blocks block-params) D)))

;; Model definitions
(define omni-tiny (define-model "omni-tiny" 32000 256 6 8 1024 0.1))
(define omni-small (define-model "omni-small" 32000 512 12 8 2048 0.1))
(define omni-base (define-model "omni-base" 32000 768 12 12 3072 0.1))
(define omni-large (define-model "omni-large" 32000 1024 24 16 4096 0.1))

;; Print model info
(define (describe-model spec)
  (display (string-append
    "Model: " (model-name spec) "\n"
    "Vocab: " (number->string (model-vocab spec)) "\n"
    "Embed: " (number->string (model-embed spec)) "\n"
    "Layers: " (number->string (/ (length (model-layers spec)) 4)) "\n"
    "Params: ~" (number->string (/ (count-parameters spec) 1000000)) "M\n")))

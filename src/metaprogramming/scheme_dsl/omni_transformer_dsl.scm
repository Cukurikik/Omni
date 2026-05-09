;; @omni-layer Metaprogramming | @omni-lang Scheme | @omni-batch 18 | @omni-semester 16
;; @omni-description Scheme macro system for transformer DSL: hygienic macros
;; for defining model architectures, attention patterns, and training configs.

;; Vector operations
(define (vec-add a b) (map + a b))
(define (vec-scale a s) (map (lambda (x) (* x s)) a))
(define (vec-dot a b) (apply + (map * a b)))
(define (vec-norm a) (sqrt (apply + (map (lambda (x) (* x x)) a))))

;; Softmax
(define (softmax xs)
  (let* ((mx (apply max xs))
         (exps (map (lambda (x) (exp (- x mx))) xs))
         (s (+ (apply + exps) 1e-10)))
    (map (lambda (e) (/ e s)) exps)))

;; Layer normalization
(define (layer-norm xs)
  (let* ((n (length xs))
         (mean (/ (apply + xs) n))
         (var (/ (apply + (map (lambda (x) (expt (- x mean) 2)) xs)) n))
         (inv-std (/ 1.0 (sqrt (+ var 1e-5)))))
    (map (lambda (x) (* (- x mean) inv-std)) xs)))

;; Attention
(define (attention q k v scale)
  (let* ((n (length q))
         (scores (map (lambda (qi)
                   (map (lambda (ki) (* (vec-dot qi ki) scale)) k)) q))
         (weights (map softmax scores)))
    (map (lambda (wi)
           (apply map + (map (lambda (w vj) (vec-scale vj w)) wi v)))
         weights)))

;; Model builder macro
(define-syntax define-transformer
  (syntax-rules (layers heads dim)
    ((_ name (layers n-layers) (heads n-heads) (dim d-model))
     (define (name input)
       (let loop ((x input) (l 0))
         (if (>= l n-layers) x
             (loop (transformer-block x d-model n-heads) (+ l 1))))))))

(define (transformer-block x d-model n-heads)
  (let* ((head-dim (quotient d-model n-heads))
         (scale (/ 1.0 (sqrt head-dim)))
         (attn-out (attention x x x scale))
         (residual (map vec-add x attn-out))
         (normed (map layer-norm residual)))
    normed))

;; Training config DSL
(define-syntax define-training
  (syntax-rules (lr epochs batch-size optimizer)
    ((_ name (lr learning-rate) (epochs n-epochs) (batch-size bs) (optimizer opt))
     (define name
       (list (cons 'lr learning-rate) (cons 'epochs n-epochs)
             (cons 'batch-size bs) (cons 'optimizer (quote opt)))))))

;; Usage: Define a 6-layer, 12-head, 768-dim transformer
(define-transformer omni-encoder (layers 6) (heads 12) (dim 768))

;; Usage: Define training config
(define-training default-training (lr 0.0001) (epochs 50) (batch-size 32) (optimizer adam))

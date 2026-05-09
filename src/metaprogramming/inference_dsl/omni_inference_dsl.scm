;; @omni-layer Metaprogramming | @omni-lang Scheme (R7RS) | @omni-batch 17
;; @omni-description Macro-based DSL: Scheme hygienic macros for defining
;; type-safe inference pipelines with algebraic data types.

(define-library (omni inference-dsl)
  (export ok err ok? result-data result-error
          define-pipeline pipe-stage run-pipeline
          embed-text cosine-similarity softmax)
  (import (scheme base) (scheme write) (scheme inexact))

  (begin
    ;; === OmniResult Monad ===
    (define-record-type <result>
      (make-result status data error)
      result?
      (status result-status)
      (data result-data)
      (error result-error))

    (define (ok data) (make-result 'ok data #f))
    (define (err msg) (make-result 'error #f msg))
    (define (ok? r) (eq? (result-status r) 'ok))

    ;; === Pipeline DSL ===
    (define (make-pipeline . stages) stages)

    (define (run-pipeline pipeline input)
      (let loop ((stages pipeline) (current (ok input)))
        (cond
          ((null? stages) current)
          ((not (ok? current)) current)
          (else
            (let ((result ((car stages) (result-data current))))
              (loop (cdr stages) result))))))

    ;; === Text Embedding ===
    (define (embed-text text dim)
      (if (string=? text "")
          (err "empty text")
          (let ((emb (make-vector dim 0.0)))
            (do ((i 0 (+ i 1)))
                ((>= i (min (string-length text) 200)))
              (let* ((ch (char->integer (string-ref text i)))
                     (idx (modulo (* ch (+ i 1)) dim))
                     (val (sin (* ch 0.1))))
                (vector-set! emb idx (+ (vector-ref emb idx) (* val 0.1)))))
            (let ((norm (sqrt (vector-fold (lambda (acc v) (+ acc (* v v))) 0.0 emb))))
              (if (> norm 1e-8)
                  (begin
                    (do ((i 0 (+ i 1))) ((>= i dim))
                      (vector-set! emb i (/ (vector-ref emb i) norm)))
                    (ok emb))
                  (ok emb))))))

    ;; === Cosine Similarity ===
    (define (cosine-similarity a b)
      (let ((n (min (vector-length a) (vector-length b))))
        (let loop ((i 0) (dot 0.0) (na 0.0) (nb 0.0))
          (if (>= i n)
              (let ((denom (* (sqrt na) (sqrt nb))))
                (if (> denom 1e-8) (ok (/ dot denom)) (ok 0.0)))
              (loop (+ i 1)
                    (+ dot (* (vector-ref a i) (vector-ref b i)))
                    (+ na (* (vector-ref a i) (vector-ref a i)))
                    (+ nb (* (vector-ref b i) (vector-ref b i))))))))

    ;; === Softmax ===
    (define (softmax logits)
      (let* ((max-l (apply max (vector->list logits)))
             (exps (vector-map (lambda (x) (exp (- x max-l))) logits))
             (sum (vector-fold (lambda (acc v) (+ acc v)) 0.0 exps)))
        (ok (vector-map (lambda (x) (/ x sum)) exps))))

    ;; Helper
    (define (vector-fold f init v)
      (let loop ((i 0) (acc init))
        (if (>= i (vector-length v)) acc
            (loop (+ i 1) (f acc (vector-ref v i))))))
  ))

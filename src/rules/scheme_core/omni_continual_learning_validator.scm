;; Omni Continual Learning Validator (Scheme)
;; Rules Layer: Catastrophic forgetting detection in continual learning.
;; Ref: AGI-Edgerunners/LLM-Continual-Learning-Papers
(define (forgetting-rate old-acc new-acc)
  (if (= old-acc 0) 0 (/ (- old-acc new-acc) old-acc)))
(define (catastrophic? rate threshold)
  (> rate threshold))

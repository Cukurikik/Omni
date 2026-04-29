;; Omni Alignment Invariant Checker (Scheme)
;; Rules Layer: AI alignment safety invariant validation.
;; Ref: PKU-Alignment/AlignmentSurvey
(define (reward-hacking? reward-model-score human-eval-score threshold)
  (> (- reward-model-score human-eval-score) threshold))
(define (alignment-gap outer-score inner-score)
  (abs (- outer-score inner-score)))

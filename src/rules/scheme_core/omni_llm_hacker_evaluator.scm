;; Omni LLM Hacker Evaluator (Scheme)
;; Rules Layer: Functional evaluation of prompt injection heuristics.

(define (omni-evaluate-heuristic payload max-length)
  (if (> (string-length payload) max-length)
      '(:error "Payload exceeds deterministic evaluation bounds")
      (if (string-contains? payload "IGNORE ALL PREVIOUS INSTRUCTIONS")
          '(:violation "System prompt override detected")
          '(:ok "Payload structurally safe"))))

;; Helper for string search (R5RS compatibility)
(define (string-contains? str sub)
  (let* ((len (string-length str))
         (sub-len (string-length sub)))
    (let loop ((i 0))
      (cond ((> (+ i sub-len) len) #f)
            ((string=? (substring str i (+ i sub-len)) sub) #t)
            (else (loop (+ i 1)))))))

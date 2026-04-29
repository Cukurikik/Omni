;; Omni LLMs4OL Taxonomy Validator (Scheme)
;; Rules Layer: Cycle detection in ontology hierarchies.
;; Ref: HamedBabaei/LLMs4OL

(define (has-cycle? graph visited node)
  (cond
    ((memq node visited) #t)
    (else
     (let ((children (assq node graph)))
       (if children
           (any (lambda (child) (has-cycle? graph (cons node visited) child)) (cdr children))
           #f)))))

(define (any pred lst)
  (cond ((null? lst) #f) ((pred (car lst)) #t) (else (any pred (cdr lst)))))

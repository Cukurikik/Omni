;; OMNI Scheme Continuation-Passing Style (CPS) Transformer
(define (cps-transform expr k)
  (cond
    ((symbol? expr) (list k expr))
    ((number? expr) (list k expr))
    ((eq? (car expr) 'lambda)
     (let ((params (cadr expr))
           (body (caddr expr))
           (k-param (gensym "k")))
       (list k `(lambda ,(append params (list k-param))
                  ,(cps-transform body k-param)))))
    (else
     (let* ((proc (car expr))
            (args (cdr expr))
            (v-proc (gensym "vp"))
            (v-args (map (lambda (x) (gensym "va")) args)))
       (cps-transform proc
                      `(lambda (,v-proc)
                         ,(let loop ((args args) (v-args v-args))
                            (if (null? args)
                                `(,v-proc ,@v-args ,k)
                                (cps-transform (car args)
                                               `(lambda (,(car v-args))
                                                  ,(loop (cdr args) (cdr v-args))))))))))))

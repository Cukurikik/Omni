;; @omni-layer Metaprogramming | @omni-lang Common Lisp | @omni-batch 17
;; @omni-description Macro system: Common Lisp metaprogramming for
;; generating type-safe inference pipeline stages at compile time.

(defpackage :omni.inference
  (:use :cl)
  (:export #:ok #:err #:ok-p #:result-data #:result-error
           #:define-stage #:run-pipeline
           #:embed-text #:cosine-similarity #:softmax))

(in-package :omni.inference)

;;; === OmniResult Monad ===
(defstruct (omni-result (:constructor make-result (status data error)))
  (status :ok :type keyword)
  (data nil)
  (error nil))

(defun ok (data) (make-result :ok data nil))
(defun err (msg) (make-result :error nil msg))
(defun ok-p (r) (eq (omni-result-status r) :ok))
(defun result-data (r) (omni-result-data r))
(defun result-error (r) (omni-result-error r))

;;; === Pipeline Stage Macro ===
(defmacro define-stage (name (input-var) &body body)
  "Define a named pipeline stage that takes input and returns OmniResult."
  `(defun ,name (,input-var)
     (handler-case
         (progn ,@body)
       (error (e) (err (format nil "Stage ~A failed: ~A" ',name e))))))

;;; === Pipeline Runner ===
(defun run-pipeline (stages input)
  "Run a sequence of stages, short-circuiting on error."
  (reduce (lambda (result stage)
            (if (ok-p result)
                (funcall stage (result-data result))
                result))
          stages
          :initial-value (ok input)))

;;; === Text Embedding ===
(defun embed-text (text dim)
  "Generate a normalized embedding vector from text."
  (if (zerop (length text))
      (err "empty text")
      (let ((emb (make-array dim :initial-element 0.0d0)))
        (loop for i from 0 below (min (length text) 200)
              for ch = (char-code (char text i))
              for idx = (mod (* ch (1+ i)) dim)
              do (incf (aref emb idx) (* (sin (* ch 0.1d0)) 0.1d0)))
        (let ((norm (sqrt (loop for v across emb sum (* v v)))))
          (when (> norm 1d-8)
            (dotimes (i dim) (setf (aref emb i) (/ (aref emb i) norm))))
          (ok emb)))))

;;; === Cosine Similarity ===
(defun cosine-similarity (a b)
  "Compute cosine similarity between two vectors."
  (let ((n (min (length a) (length b))))
    (let ((dot 0.0d0) (na 0.0d0) (nb 0.0d0))
      (dotimes (i n)
        (incf dot (* (aref a i) (aref b i)))
        (incf na (* (aref a i) (aref a i)))
        (incf nb (* (aref b i) (aref b i))))
      (let ((denom (* (sqrt na) (sqrt nb))))
        (if (> denom 1d-8)
            (ok (/ dot denom))
            (ok 0.0d0))))))

;;; === Softmax ===
(defun softmax (logits)
  "Compute softmax of a vector."
  (let* ((max-l (reduce #'max logits))
         (exps (map 'vector (lambda (x) (exp (- x max-l))) logits))
         (sum-e (reduce #'+ exps)))
    (ok (map 'vector (lambda (x) (/ x sum-e)) exps))))

;;; === Pre-built stages ===
(define-stage tokenize (text)
  (ok (coerce (split-sequence #\Space text) 'vector)))

(define-stage classify-sentiment (embedding)
  (let* ((logits (make-array 5 :initial-contents
                  (loop for c from 0 below 5
                        collect (loop for j from 0 below (min 32 (length embedding))
                                      sum (* (aref embedding j) (sin (* (1+ c) (1+ j) 0.01d0)))))))
         (probs (result-data (softmax logits)))
         (best-idx (position (reduce #'max probs) probs)))
    (ok (list :label (nth best-idx '(:very-neg :neg :neutral :pos :very-pos))
              :confidence (aref probs best-idx)))))

(defun split-sequence (delimiter string)
  (loop for start = 0 then (1+ pos)
        for pos = (position delimiter string :start start)
        collect (subseq string start (or pos (length string)))
        while pos))

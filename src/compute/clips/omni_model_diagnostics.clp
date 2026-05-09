; OMNI NL/Rules Layer — CLIPS Expert System for Model Diagnostics
; Rule-based diagnostics for transformer model issues.

(deftemplate model-status
  (slot name (type STRING))
  (slot architecture (type STRING))
  (slot accuracy (type FLOAT))
  (slot latency-ms (type FLOAT))
  (slot memory-mb (type FLOAT))
  (slot loss (type FLOAT))
  (slot gradient-norm (type FLOAT))
  (slot status (type SYMBOL) (allowed-values healthy degraded critical)))

(deftemplate diagnostic
  (slot model (type STRING))
  (slot severity (type SYMBOL) (allowed-values info warning critical))
  (slot category (type STRING))
  (slot message (type STRING))
  (slot recommendation (type STRING)))

; Rule: Detect training instability (exploding gradients)
(defrule exploding-gradients
  (model-status (name ?name) (gradient-norm ?gn&:(> ?gn 10.0)))
  =>
  (assert (diagnostic
    (model ?name) (severity critical) (category "training")
    (message (str-cat "Gradient norm " ?gn " exceeds threshold (10.0)"))
    (recommendation "Reduce learning rate or enable gradient clipping (max_norm=1.0)"))))

; Rule: Detect high latency
(defrule high-latency
  (model-status (name ?name) (latency-ms ?lat&:(> ?lat 500.0)))
  =>
  (assert (diagnostic
    (model ?name) (severity warning) (category "performance")
    (message (str-cat "Inference latency " ?lat "ms exceeds 500ms threshold"))
    (recommendation "Enable KV-cache, apply quantization (INT8), or reduce max_seq_len"))))

; Rule: Detect accuracy degradation
(defrule accuracy-drop
  (model-status (name ?name) (accuracy ?acc&:(< ?acc 0.80)))
  =>
  (assert (diagnostic
    (model ?name) (severity critical) (category "quality")
    (message (str-cat "Accuracy " ?acc " below minimum threshold (0.80)"))
    (recommendation "Retrain with more data, check for data drift, or rollback to previous version"))))

; Rule: Memory pressure
(defrule memory-pressure
  (model-status (name ?name) (memory-mb ?mem&:(> ?mem 30000.0)))
  =>
  (assert (diagnostic
    (model ?name) (severity warning) (category "resources")
    (message (str-cat "Memory usage " ?mem "MB approaching GPU VRAM limit"))
    (recommendation "Apply model pruning, enable gradient checkpointing, or use model parallelism"))))

; Rule: Loss plateau detection
(defrule loss-plateau
  (model-status (name ?name) (loss ?l&:(> ?l 2.0)) (status healthy))
  =>
  (assert (diagnostic
    (model ?name) (severity info) (category "training")
    (message (str-cat "Training loss " ?l " may indicate plateau"))
    (recommendation "Try cosine annealing scheduler, increase warmup, or adjust batch size"))))

; Rule: Model is healthy
(defrule model-healthy
  (model-status (name ?name) (accuracy ?acc&:(>= ?acc 0.90))
                (latency-ms ?lat&:(< ?lat 200.0))
                (gradient-norm ?gn&:(< ?gn 5.0)))
  =>
  (assert (diagnostic
    (model ?name) (severity info) (category "status")
    (message "Model is operating within healthy parameters")
    (recommendation "Continue monitoring. Consider A/B testing for further improvements."))))

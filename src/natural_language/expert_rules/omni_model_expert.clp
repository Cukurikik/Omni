; @omni-layer NaturalLanguage | @omni-lang CLIPS | @omni-batch 17
; @omni-description Expert system rules: CLIPS rule engine for automated
; model selection, deployment recommendations, and performance diagnosis.

(defmodule OMNI-EXPERT (export ?ALL))

;; === Templates ===
(deftemplate model-request
    (slot task-type (type SYMBOL) (allowed-symbols classification ner sentiment generation translation))
    (slot language (type SYMBOL) (default en))
    (slot max-latency-ms (type INTEGER) (default 100))
    (slot max-memory-mb (type INTEGER) (default 4096))
    (slot accuracy-priority (type SYMBOL) (allowed-symbols low medium high) (default high))
)

(deftemplate available-model
    (slot model-id (type SYMBOL))
    (slot name (type STRING))
    (slot task-type (type SYMBOL))
    (slot latency-ms (type INTEGER))
    (slot memory-mb (type INTEGER))
    (slot accuracy (type FLOAT) (range 0.0 1.0))
    (slot languages (type STRING)) ;; comma-separated
    (slot status (type SYMBOL) (allowed-symbols active inactive degraded))
)

(deftemplate recommendation
    (slot model-id (type SYMBOL))
    (slot reason (type STRING))
    (slot confidence (type FLOAT))
    (slot priority (type INTEGER))
)

(deftemplate diagnosis
    (slot issue (type SYMBOL))
    (slot severity (type SYMBOL) (allowed-symbols low medium high critical))
    (slot description (type STRING))
    (slot action (type STRING))
)

;; === Model Selection Rules ===
(defrule select-best-model
    "Select model matching task requirements"
    (model-request (task-type ?task) (max-latency-ms ?max-lat) (max-memory-mb ?max-mem) (accuracy-priority ?acc-pri))
    (available-model (model-id ?id) (name ?name) (task-type ?task) (latency-ms ?lat) (memory-mb ?mem) (accuracy ?acc) (status active))
    (test (<= ?lat ?max-lat))
    (test (<= ?mem ?max-mem))
    =>
    (bind ?conf (/ ?acc 1.0))
    (if (eq ?acc-pri high) then (bind ?conf (* ?conf 1.2)))
    (assert (recommendation (model-id ?id) (reason (str-cat "Model " ?name " matches task " ?task " within constraints")) (confidence (min ?conf 1.0)) (priority 1)))
)

(defrule high-latency-fallback
    "Suggest lighter model when primary exceeds latency"
    (model-request (task-type ?task) (max-latency-ms ?max-lat))
    (available-model (model-id ?id) (task-type ?task) (latency-ms ?lat) (status active))
    (test (> ?lat ?max-lat))
    (available-model (model-id ?alt-id) (task-type ?task) (latency-ms ?alt-lat) (status active))
    (test (<= ?alt-lat ?max-lat))
    (test (neq ?id ?alt-id))
    =>
    (assert (recommendation (model-id ?alt-id) (reason (str-cat "Fallback: primary model exceeds " ?max-lat "ms latency")) (confidence 0.7) (priority 2)))
)

;; === Performance Diagnosis Rules ===
(defrule diagnose-high-latency
    "Detect high latency models"
    (available-model (model-id ?id) (name ?name) (latency-ms ?lat))
    (test (> ?lat 500))
    =>
    (assert (diagnosis (issue high-latency) (severity high) (description (str-cat ?name " latency: " ?lat "ms exceeds 500ms threshold")) (action "Consider model quantization or batch optimization")))
)

(defrule diagnose-memory-pressure
    "Detect memory-heavy models"
    (available-model (model-id ?id) (name ?name) (memory-mb ?mem))
    (test (> ?mem 8192))
    =>
    (assert (diagnosis (issue memory-pressure) (severity medium) (description (str-cat ?name " uses " ?mem "MB exceeding 8GB")) (action "Enable model sharding or use distilled variant")))
)

(defrule diagnose-degraded-model
    "Alert on degraded model status"
    (available-model (model-id ?id) (name ?name) (status degraded))
    =>
    (assert (diagnosis (issue degraded-service) (severity critical) (description (str-cat ?name " is in degraded state")) (action "Restart inference pod or failover to backup")))
)

;; === Auto-scaling Rule ===
(defrule suggest-scale-up
    "Suggest scaling when all models are busy"
    (not (available-model (status active) (latency-ms ?lat&:(< ?lat 100))))
    =>
    (assert (diagnosis (issue capacity-exhausted) (severity high) (description "No low-latency models available") (action "Trigger auto-scale: increase GPU instance count")))
)

# @omni-layer Natural Language | @omni-lang CLIPS | @omni-batch 18 | @omni-semester 16
# @omni-description CLIPS expert rules for transformer model health diagnosis:
# automated anomaly detection, performance degradation alerts, and remediation.

(deftemplate model-status
   (slot model-id (type STRING))
   (slot avg-latency-ms (type FLOAT))
   (slot p95-latency-ms (type FLOAT))
   (slot error-rate (type FLOAT))
   (slot gpu-utilization (type FLOAT))
   (slot memory-usage-pct (type FLOAT))
   (slot throughput-rps (type FLOAT))
   (slot queue-depth (type INTEGER))
   (slot status (type SYMBOL) (allowed-symbols healthy degraded critical unknown)))

(deftemplate diagnosis
   (slot model-id (type STRING))
   (slot issue (type STRING))
   (slot severity (type SYMBOL) (allowed-symbols info warning critical))
   (slot recommendation (type STRING))
   (slot timestamp (type STRING)))

;; Rule: High latency detection
(defrule detect-high-latency
   (model-status (model-id ?id) (p95-latency-ms ?lat&:(> ?lat 500.0)) (status ~critical))
   =>
   (assert (diagnosis
      (model-id ?id)
      (issue "P95 latency exceeds 500ms threshold")
      (severity warning)
      (recommendation "Consider scaling inference replicas or optimizing batch size")
      (timestamp (str-cat (time))))))

;; Rule: Critical latency
(defrule detect-critical-latency
   (model-status (model-id ?id) (p95-latency-ms ?lat&:(> ?lat 2000.0)))
   =>
   (assert (diagnosis
      (model-id ?id)
      (issue "P95 latency exceeds 2000ms - CRITICAL")
      (severity critical)
      (recommendation "Immediately investigate: check GPU memory, model loading, or network issues")
      (timestamp (str-cat (time))))))

;; Rule: High error rate
(defrule detect-high-error-rate
   (model-status (model-id ?id) (error-rate ?er&:(> ?er 0.05)))
   =>
   (assert (diagnosis
      (model-id ?id)
      (issue (str-cat "Error rate " (format nil "%.1f%%" (* ?er 100)) " exceeds 5% threshold"))
      (severity critical)
      (recommendation "Check model health, input validation, and OOM errors")
      (timestamp (str-cat (time))))))

;; Rule: GPU underutilization
(defrule detect-gpu-underutil
   (model-status (model-id ?id) (gpu-utilization ?gpu&:(< ?gpu 30.0)) (throughput-rps ?rps&:(> ?rps 0)))
   =>
   (assert (diagnosis
      (model-id ?id)
      (issue "GPU utilization below 30% - inefficient resource usage")
      (severity info)
      (recommendation "Increase batch size or enable continuous batching to improve GPU utilization")
      (timestamp (str-cat (time))))))

;; Rule: Memory pressure
(defrule detect-memory-pressure
   (model-status (model-id ?id) (memory-usage-pct ?mem&:(> ?mem 90.0)))
   =>
   (assert (diagnosis
      (model-id ?id)
      (issue "Memory usage above 90% - risk of OOM")
      (severity warning)
      (recommendation "Reduce batch size, enable KV-cache paging, or use quantized model")
      (timestamp (str-cat (time))))))

;; Rule: Queue buildup
(defrule detect-queue-buildup
   (model-status (model-id ?id) (queue-depth ?q&:(> ?q 100)))
   =>
   (assert (diagnosis
      (model-id ?id)
      (issue (str-cat "Request queue depth " ?q " - backpressure detected"))
      (severity warning)
      (recommendation "Scale out inference workers or implement request shedding")
      (timestamp (str-cat (time))))))

;; Rule: Healthy model confirmation
(defrule confirm-healthy
   (model-status (model-id ?id) (p95-latency-ms ?lat&:(< ?lat 200.0))
                 (error-rate ?er&:(< ?er 0.01))
                 (gpu-utilization ?gpu&:(> ?gpu 50.0)))
   =>
   (assert (diagnosis
      (model-id ?id)
      (issue "All metrics within healthy thresholds")
      (severity info)
      (recommendation "No action required - model operating normally")
      (timestamp (str-cat (time))))))

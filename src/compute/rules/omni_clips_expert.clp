; OMNI Natural Language & Rules Layer
; CLIPS Expert System Rules for Hardware Routing
; Uses forward-chaining inference to dynamically allocate GPU/CPU loads 

(deftemplate inference-request
   (slot id (type SYMBOL))
   (slot complexity (type INTEGER)) ; 1 to 10
   (slot precision (type SYMBOL))   ; fp32, fp16, int8
   (slot latency-req (type INTEGER))) ; milliseconds

(deftemplate hardware-node
   (slot type (type SYMBOL))        ; gpu_a100, gpu_t4, cpu_avx512
   (slot available (type SYMBOL))   ; yes, no
   (slot queue-depth (type INTEGER)))

; Rule: High complexity, low latency -> Route to A100 GPU
(defrule route-high-priority-gpu
   ?req <- (inference-request (id ?id) (complexity ?c&:(> ?c 7)) (latency-req ?l&:(< ?l 100)))
   ?node <- (hardware-node (type gpu_a100) (available yes) (queue-depth ?qd&:(< ?qd 5)))
   =>
   (printout t "OMNI ROUTER: Dispatching Request " ?id " to A100 GPU Node. Queue depth: " ?qd crlf)
   (modify ?node (queue-depth (+ ?qd 1)))
   (retract ?req))

; Rule: Quantized precision, background task -> Route to CPU AVX-512
(defrule route-quantized-cpu
   ?req <- (inference-request (id ?id) (precision int8) (latency-req ?l&:(> ?l 500)))
   ?node <- (hardware-node (type cpu_avx512) (available yes))
   =>
   (printout t "OMNI ROUTER: Dispatching Request " ?id " to CPU AVX-512 Node." crlf)
   (modify ?node (queue-depth (+ (fact-slot-value ?node queue-depth) 1)))
   (retract ?req))

; Rule: Fallback route to T4 if A100 is busy
(defrule route-fallback-t4
   ?req <- (inference-request (id ?id) (complexity ?c&:(> ?c 5)))
   (not (hardware-node (type gpu_a100) (available yes) (queue-depth ?qd&:(< ?qd 5))))
   ?node <- (hardware-node (type gpu_t4) (available yes) (queue-depth ?qdt4&:(< ?qdt4 10)))
   =>
   (printout t "OMNI ROUTER: A100 overloaded. Fallback Dispatch Request " ?id " to T4 GPU." crlf)
   (modify ?node (queue-depth (+ ?qdt4 1)))
   (retract ?req))

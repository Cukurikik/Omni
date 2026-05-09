; OMNI NLP — CLIPS Expert System Rules
; Hardware Diagnostic Expert System for OMNI Nodes

(defrule check-gpu-temperature
   (gpu (id ?id) (temperature ?temp&:(> ?temp 85)))
   =>
   (printout t "WARNING: GPU " ?id " is overheating (" ?temp "C). Throttling required." crlf)
   (assert (action (type throttle) (target ?id))))

(defrule check-memory-errors
   (gpu (id ?id) (ecc-errors ?errors&:(> ?errors 100)))
   =>
   (printout t "CRITICAL: GPU " ?id " exhibiting high ECC errors. Recommend hardware replacement." crlf)
   (assert (action (type offline-node) (target ?id))))

(defrule execute-throttle
   ?a <- (action (type throttle) (target ?id))
   =>
   (printout t "EXECUTING: Throttling GPU " ?id " to 50% power limit." crlf)
   (retract ?a))

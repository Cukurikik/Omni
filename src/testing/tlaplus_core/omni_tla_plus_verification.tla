---- MODULE OmniVerification ----
VARIABLES state
Init == state = "ready"
Next == state' = "running"
====

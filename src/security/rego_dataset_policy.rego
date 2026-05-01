package omni.security.dataset

default allow = false

allow {
    input.action == "read"
    input.dataset.classification == "public"
}

allow {
    input.action == "write"
    input.user.role == "researcher"
    input.dataset.size_mb < 500000 # Max 500GB limit for training set uploads
}

deny[msg] {
    input.dataset.contains_pii == true
    input.action == "train"
    msg := "Training on datasets containing PII is strictly forbidden by Omni framework bounds."
}

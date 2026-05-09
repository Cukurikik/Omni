package omni.security.transformers

# Transformer Policy: Open Policy Agent (OPA) rules for controlling
# execution boundaries on massive transformer inference tasks.

default allow_inference = false

# Allow inference if the user has a valid quota and the model is within memory bounds
allow_inference {
    input.user.role == "researcher"
    input.model.sequence_length <= 32768
    input.model.precision == "fp16"
}

# Admins can override and run massive sequence lengths (e.g., ParsBigBird)
allow_inference {
    input.user.role == "admin"
}

# Deny highly destructive generation parameters
deny_generation[msg] {
    input.generation.temperature > 2.0
    msg := "Temperature parameter exceeds safety threshold of 2.0"
}

deny_generation[msg] {
    input.generation.max_tokens > 100000
    msg := "Max tokens exceeds the physical cluster capacity"
}

# Crossmodal authorization check
allow_crossmodal_training {
    input.dataset.modality == "video_text"
    input.cluster.available_gpus >= 8
    input.user.clearance == "level_4"
}

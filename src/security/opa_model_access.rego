package omni.model.access

default allow = false

# Restrict model access based on physical VRAM requirements
allow {
    input.user.role == "researcher"
    input.model.vram_requirements_gb <= 80
}

allow {
    input.user.role == "lead_engineer"
    input.model.vram_requirements_gb <= 320 # Multi-GPU cluster access
}

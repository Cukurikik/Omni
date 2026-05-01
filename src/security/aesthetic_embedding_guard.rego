package omni.security.aesthetic

# @omni_bridge_security
# OMNI MOTHER SYSTEM - BATCH 18
# Repository: MushroomFleet/djz-Aesthetic-Embeddings
# Layer: Security & Policy Layer
# Domain: Aesthetic Image Embedding Limits and Tensor Guardrails

# Default fail-secure architecture
default allow_embedding_generation = false
default allow_tensor_allocation = false

# Validate the dimensions to prevent OOM DOS attacks on the GPU inference server
valid_dimensions {
    input.width >= 256
    input.width <= 2048
    input.height >= 256
    input.height <= 2048
    
    # Check max pixel limit (e.g., 1024x1024 = 1,048,576 pixels) to enforce physical VRAM limits
    total_pixels := input.width * input.height
    total_pixels <= 1048576
}

# Validate embedding scale vector constraint (CFG scale equivalent limits)
valid_embedding_scale {
    input.aesthetic_scale >= 0.0
    input.aesthetic_scale <= 20.0
}

# Authorize embedding generation only if bounds are physically safe
allow_embedding_generation {
    valid_dimensions
    valid_embedding_scale
    
    # Must provide explicit system role clearance
    input.role == "vision_compute_node"
}

# Authorize VRAM allocation for the embedding tensors
allow_tensor_allocation {
    allow_embedding_generation
    input.requested_vram_mb <= 8192 # Strict 8GB limit per job constraint
}

# Check against blocked tags (Content Safety Filter)
blocked_tags := {"nsfw", "gore", "illegal", "violence"}

contains_blocked_tag {
    some i
    input.prompt_tags[i] == blocked_tags[_]
}

# Final approval requires passing all safety filters
is_safe_prompt {
    not contains_blocked_tag
}

# The ultimate entrypoint policy bridging domain and infrastructure
default execute_pipeline = false
execute_pipeline {
    allow_tensor_allocation
    is_safe_prompt
}

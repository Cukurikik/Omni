package omni.security.deepspeed

# OMNI DEEPSPEED: Tensor Distribution Authorization
# Rego policy to enforce secure communication limits between ZeRO optimizer ranks.
# Source: microsoft/DeepSpeed

default allow_tensor_sync = false

# Allow sync if the nodes belong to the same logical cluster and training run
allow_tensor_sync {
    input.source_node.cluster_id == input.dest_node.cluster_id
    input.source_node.run_id == input.dest_node.run_id
    is_valid_rank(input.dest_node.rank)
}

is_valid_rank(rank) {
    # Assuming the world size is passed in the context
    rank >= 0
    rank < input.world_size
}

# Deny sync of explicitly marked sensitive tensors (e.g. custom user embeddings)
# to worker nodes unless they have the 'secure_enclave' tag
deny[msg] {
    input.tensor.is_sensitive == true
    not has_secure_enclave(input.dest_node)
    msg := "Sensitive tensor sync blocked: Destination node lacks secure_enclave clearance."
}

has_secure_enclave(node) {
    node.tags[_] == "secure_enclave"
}

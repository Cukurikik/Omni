package omni.fedml.auth

# OMNI FEDML: Open Policy Agent (OPA) RBAC
# Rego policies to control which federated nodes can push gradients to the global model.
# Source: FedML-AI/FedML

default allow = false

# Allow access if the node is actively registered and has the 'federation_writer' role
allow {
    input.method == "PUSH_GRADIENTS"
    is_active_node(input.node_id)
    has_role(input.node_id, "federation_writer")
    valid_model_signature(input.payload.signature)
}

# Deny access if compute capacity dropped below threshold (evaluated via metadata)
deny[msg] {
    input.method == "PUSH_GRADIENTS"
    input.metadata.compute_capacity < 100
    msg := "Compute capacity insufficient for global aggregation."
}

# Helper rules
is_active_node(node_id) {
    # In production, this data comes from the C# Domain Layer / DB via OPA data injection
    data.active_nodes[node_id].status == "Active"
}

has_role(node_id, role) {
    data.active_nodes[node_id].roles[_] == role
}

valid_model_signature(signature) {
    # Simple check for demo purposes
    startswith(signature, "omni_sig_")
}

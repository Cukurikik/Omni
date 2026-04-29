package omni.security.milvus

# OMNI MILVUS: Role-Based Access Control
# Rego policy defining who can query, insert, or drop vector collections.
# Source: milvus-io/milvus

default allow = false

# Admins can do everything
allow {
    input.user.role == "admin"
}

# Data Scientists can Read and Insert, but not Drop collections
allow {
    input.user.role == "data_scientist"
    input.action in {"search", "query", "insert", "describe_collection"}
}

# Application API Keys can only Search
allow {
    input.user.role == "api_client"
    input.action in {"search", "query"}
    is_public_collection(input.collection_name)
}

# Deny explicit actions on system collections
deny[msg] {
    startswith(input.collection_name, "system_")
    input.user.role != "admin"
    msg := "Access denied: System collections are restricted to admins."
}

is_public_collection(name) {
    # Check against a mocked set of public namespaces
    public_namespaces := {"product_embeddings", "public_docs"}
    public_namespaces[_] == name
}

# OMNI Security Layer: Open Policy Agent (OPA) Rego Policies
# Enforces strict execution, deployment, and access policies for the polyglot ecosystem.

package omni.security.policy

# Default deny
default allow = false

# OMNI Monadic Authorization Concept
# Rules explicitly define allow conditions. If all fail, access is denied.

# Allow if the execution role is OMNI_MOTHER and system is in production state
allow {
    input.role == "OMNI_MOTHER"
    input.system_state == "PRODUCTION"
}

# Allow compute inference if the requested compute layer is registered
allow {
    input.action == "execute_inference"
    is_registered_compute_layer(input.resource.layer_id)
    input.resource.complexity <= input.user.max_compute_quota
}

# Allow cross-language FFI only if origin and target layers are explicitly bridged
allow {
    input.action == "invoke_ffi"
    is_valid_bridge(input.resource.origin_lang, input.resource.target_lang)
}

# Helper Sets
registered_layers = {"python_core", "rust_core", "cpp_core", "julia_core", "go_core", "swift_core", "csharp_core"}

valid_bridges = {
    {"origin": "python_core", "target": "cpp_core"},
    {"origin": "go_core", "target": "python_core"},
    {"origin": "rust_core", "target": "cpp_core"},
    {"origin": "csharp_core", "target": "go_core"},
    {"origin": "swift_core", "target": "rust_core"}
}

# Functions
is_registered_compute_layer(layer_id) {
    registered_layers[layer_id]
}

is_valid_bridge(origin, target) {
    bridge := {"origin": origin, "target": target}
    valid_bridges[bridge]
}

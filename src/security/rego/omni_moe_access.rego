package omni.moe.authz

# OMNI MOTHER: Security & Policy Layer (Open Policy Agent)
# Secures access to the MoE routing plane

default allow = false

# Allow admin services to re-route traffic
allow {
    input.role == "admin"
    input.action == "reroute"
}

# Allow expert nodes to register themselves
allow {
    input.role == "expert_node"
    input.action == "register"
    startswith(input.ip, "10.0.") # Internal network only
}

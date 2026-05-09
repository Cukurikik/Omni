# OMNI Framework - OPA Policy for AthenaOS Inter-Agent Authorization
package omni.athena.authz

default allow = false

# Allow agents to communicate if they belong to the same swarm group
allow {
    input.sender.group_id == input.receiver.group_id
    input.action == "message_exchange"
}

# Allow agents to offload tasks only to agents with idle capacity
allow {
    input.action == "task_offload"
    input.receiver.status == "IDLE"
    input.receiver.clearance_level >= input.task.required_clearance
}

# Prevent nodes from exceeding maximum computational load
deny {
    input.action == "task_offload"
    input.receiver.load_percentage > 90
}

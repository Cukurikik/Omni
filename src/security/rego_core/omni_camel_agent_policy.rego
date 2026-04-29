# Omni CAMEL Agent Policy (Rego/OPA)
# Ref: camel-ai/multi-agent-streamlit-ui
package omni.camel_policy
default allow_delegation = false
allow_delegation {
    input.agent_role in {"planner", "assistant", "critic"}
    input.message_length > 0
    input.message_length <= 4096
}
deny_delegation[msg] {
    input.message_length > 4096
    msg := "Message exceeds maximum length for agent delegation"
}

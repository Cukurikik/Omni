# Omni Human-Agent Trust Policy (Rego/OPA)
# Ref: HenryPengZou/Awesome-Human-Agent-Collaboration
package omni.human_agent_policy
default allow_autonomous = false
allow_autonomous {
    input.agent_confidence >= 0.8
    input.task_risk_level in {"low", "medium"}
    input.human_oversight_available
}
escalate_to_human[msg] {
    input.agent_confidence < 0.6
    msg := "Low confidence requires human review"
}
escalate_to_human[msg] {
    input.task_risk_level == "critical"
    msg := "Critical tasks require human approval"
}

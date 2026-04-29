# Omni SelfAware Model Policy (Rego/OPA)
# Ref: yinzhangyue/SelfAware
package omni.selfaware_policy
default allow_response = false
allow_response {
    input.answerable == true
    input.confidence >= 0.3
}
abstain_response[msg] {
    input.answerable == false
    msg := sprintf("Model abstained: confidence=%v below threshold", [input.confidence])
}

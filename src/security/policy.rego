# OMNI Security & Policy Layer - Rego OPA
package omni.authz

import future.keywords.in

default allow := false

# OMNI Production Rule: Allow execution only if agent has clearance and is verified
allow {
    input.agent.clearance == "level_omega"
    input.request.action in ["deploy_model", "mutate_ast"]
    input.system.verified == true
}

# Monadic error reflection via structured deny reasons
deny[msg] {
    not allow
    msg := "OMNI_ERR_UNAUTHORIZED: Agent lacks Omega-level clearance or action is restricted."
}

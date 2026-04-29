package omni.security.seldon

# OMNI Rego Security Layer: Seldon Model Access Policy
# Strictly controls which roles can deploy, modify, or route traffic to ML models.

default allow = false

# Allow system admins full access
allow {
    input.user.roles[_] == "omni-cluster-admin"
}

# Allow Data Scientists to deploy models to their namespace
allow {
    input.action == "deploy"
    input.resource.type == "seldon-deployment"
    input.user.roles[_] == "data-scientist"
    input.resource.namespace == input.user.department
}

# Only MLOps engineers can adjust traffic routing (Canary/AB)
allow {
    input.action == "adjust_traffic"
    input.resource.type == "seldon-deployment"
    input.user.roles[_] == "mlops-engineer"
}

# Deny any deployment of models requesting GPU limits exceeding quota
deny[msg] {
    input.action == "deploy"
    input.resource.gpu_requested > 4
    not input.user.roles[_] == "omni-cluster-admin"
    msg = "Deployment denied: GPU request exceeds the maximum quota of 4 per deployment."
}

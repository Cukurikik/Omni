# OMNI Security - Fine-Tune Access Policy (Rego/OPA)
package finetune.authz

default allow = false

allow {
    input.action == "read"
    input.resource.type == "experiment"
}

allow {
    input.action == "create"
    input.resource.type == "experiment"
    input.user.role == "ml_engineer"
}

allow {
    input.action == "cancel"
    input.resource.type == "experiment"
    input.user.id == input.resource.owner_id
}

allow {
    input.action == "delete"
    input.resource.type == "checkpoint"
    input.user.role == "admin"
}

allow {
    input.action == "deploy"
    input.resource.type == "model"
    input.user.role == "ml_engineer"
    input.resource.status == "completed"
    input.resource.eval_loss < 0.5
}

deny[msg] {
    input.action == "deploy"
    input.resource.eval_loss >= 0.5
    msg := sprintf("Model eval_loss %f exceeds deployment threshold 0.5", [input.resource.eval_loss])
}

deny[msg] {
    input.action == "create"
    input.resource.config.learning_rate > 0.01
    msg := "Learning rate exceeds safe maximum of 0.01"
}

gpu_budget_check {
    input.resource.config.batch_size * input.resource.config.gradient_accum_steps <= 256
}

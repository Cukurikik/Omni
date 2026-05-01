# OMNI Security - Fine-Tune Deployment Gate Policy (Rego/OPA)
package finetune.deployment_gate

default allow_deploy = false
default allow_train = false

allow_train {
    input.user.role == "ml_engineer"
    input.resource.config.learning_rate <= 0.01
    input.resource.config.batch_size <= 128
    input.resource.config.num_epochs <= 50
    gpu_budget_ok
}

allow_train {
    input.user.role == "admin"
}

gpu_budget_ok {
    input.resource.config.batch_size * input.resource.config.gradient_accum_steps <= 256
    input.resource.config.num_gpus <= input.quota.max_gpus
}

allow_deploy {
    input.resource.status == "completed"
    input.resource.best_eval_loss < 0.5
    input.resource.best_eval_acc > 0.7
    input.user.role == "ml_engineer"
    safety_checks_passed
}

allow_deploy {
    input.user.role == "admin"
    input.resource.status == "completed"
}

safety_checks_passed {
    not contains_pii(input.resource.dataset_name)
    input.resource.safety_score >= 0.9
}

contains_pii(name) {
    pii_patterns := ["ssn", "credit_card", "password", "secret"]
    some p
    pii_patterns[p]
    contains(lower(name), pii_patterns[p])
}

deny_reasons[msg] {
    input.resource.best_eval_loss >= 0.5
    msg := sprintf("Eval loss %f exceeds threshold 0.5", [input.resource.best_eval_loss])
}

deny_reasons[msg] {
    input.resource.best_eval_acc < 0.7
    msg := sprintf("Eval accuracy %f below threshold 0.7", [input.resource.best_eval_acc])
}

deny_reasons[msg] {
    input.resource.config.learning_rate > 0.01
    msg := "Learning rate exceeds safe maximum 0.01"
}

deny_reasons[msg] {
    not gpu_budget_ok
    msg := "GPU budget exceeded"
}

lower(s) = output {
    output := s
}

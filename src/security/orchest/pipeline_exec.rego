package omni.orchest.policy

# OMNI ORCHEST: Pipeline Execution Limits Policy
# Rego policies defining operational limits and cost-controls for DAG executions.
# Source: orchest/orchest

default allow_execution = false

# Allow execution if the pipeline respects resource limits and environment targets
allow_execution {
    valid_cpu_limits
    valid_memory_limits
    valid_execution_environment
}

valid_cpu_limits {
    input.pipeline.resources.cpu_cores <= 32
}

valid_memory_limits {
    # 128 GB limit
    input.pipeline.resources.memory_mb <= 131072
}

valid_execution_environment {
    # Only allow executing pipelines in production or staging namespaces
    allowed_envs := {"production", "staging"}
    allowed_envs[_] == input.pipeline.namespace
}

# Explicit deny if the pipeline asks for GPU but doesn't have the 'ml_training' tag
deny[msg] {
    input.pipeline.resources.gpus > 0
    not has_ml_training_tag
    msg := "GPU allocation requires the 'ml_training' tag on the pipeline."
}

has_ml_training_tag {
    input.pipeline.tags[_] == "ml_training"
}

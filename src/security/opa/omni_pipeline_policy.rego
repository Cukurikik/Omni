# OMNI Framework - OPA Rego Policy for Oreilly AI Pipelines Access
package omni.pipeline.authz

default allow = false

# Allow pipeline execution if user is an admin
allow {
    input.user.role == "admin"
}

# Allow data scientists to execute specific approved pipelines
allow {
    input.user.role == "data_scientist"
    input.request.action == "execute"
    input.request.pipeline_name == approved_pipelines[_]
}

# Approved pipelines for data scientists
approved_pipelines = [
    "default_llm_pipeline",
    "feature_extraction_pipeline",
    "summarization_pipeline"
]

# Deny access to production deployment pipelines for non-admins
deny {
    input.request.action == "deploy_to_prod"
    input.user.role != "admin"
}

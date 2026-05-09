package omni.chimera.pipeline

default allow = false

allow {
    input.role == "pipeline_admin"
    input.action == "schedule_microbatch"
}

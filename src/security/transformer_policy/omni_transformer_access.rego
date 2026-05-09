# @omni-layer Security | @omni-lang Rego | @omni-batch 18 | @omni-semester 16
# @omni-description OPA policies for transformer model access control:
# governs who can access which models, enforce rate limits, and audit usage.

package omni.transformer.access

import rego.v1

default allow := false

# Role-based model access
allow if {
    input.action == "inference"
    has_model_access
    within_rate_limit
    valid_api_key
}

allow if {
    input.action == "train"
    input.user.role in {"admin", "ml_engineer", "researcher"}
    valid_api_key
}

allow if {
    input.action == "edit_knowledge"
    input.user.role in {"admin", "knowledge_curator"}
    valid_edit_target
}

allow if {
    input.action == "explain"
    has_model_access
}

has_model_access if {
    model_permissions[input.model_id][input.user.role]
}

model_permissions := {
    "tempo-forecaster": {"admin": true, "analyst": true, "ml_engineer": true},
    "hiformer-segmentor": {"admin": true, "radiologist": true, "ml_engineer": true},
    "video-classifier": {"admin": true, "content_moderator": true, "ml_engineer": true},
    "bert-ner": {"admin": true, "analyst": true, "developer": true},
    "knowledge-editor": {"admin": true, "knowledge_curator": true},
    "long-text-classifier": {"admin": true, "analyst": true, "developer": true},
    "weight-sync": {"admin": true, "ml_engineer": true},
}

within_rate_limit if {
    input.request_count <= rate_limits[input.user.tier]
}

rate_limits := {
    "free": 100,
    "pro": 10000,
    "enterprise": 1000000,
    "unlimited": 999999999,
}

valid_api_key if {
    input.api_key != ""
    startswith(input.api_key, "omni_")
    count(input.api_key) >= 32
}

valid_edit_target if {
    input.edit.subject != ""
    input.edit.new_object != ""
    input.edit.relation != ""
}

# Audit decision
audit_log[entry] if {
    entry := {
        "user": input.user.id,
        "action": input.action,
        "model": input.model_id,
        "allowed": allow,
        "timestamp": input.timestamp,
    }
}

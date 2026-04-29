package randopt.routing

default route_to_expert = false

route_to_expert {
    input.token_type == "math"
    input.expert_load < 0.9
}

omni_result = {
    "value": route_to_expert,
    "error": null,
    "is_ok": true
}

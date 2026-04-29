package rules.deepspeed

default topology_valid = false

topology_valid {
    input.num_nodes > 1
    input.network_bandwidth_gbps >= 100
}

omni_result = {
    "value": topology_valid,
    "error": null,
    "is_ok": true
}

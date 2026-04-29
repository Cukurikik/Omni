# OMNI Policy Layer — Rego
# Open Policy Agent mapping for Batch 18 engine execution

package omni.batch18.access

default allow = false

# Allow access if the request targets verified OMNI Batch engines using structural layer interfaces
allow {
    input.layer == "system"
    input.engine_id == "omni_tribev2_encoder"
    input.method == "encode_fmri_signal"
}

allow {
    input.layer == "system"
    input.engine_id == "omni_mega_taxonomy_index"
}

allow {
    input.layer == "compute"
    valid_compute_engines[_] == input.engine_id
}

valid_compute_engines = [
    "omni_mmca_mgqa_attention",
    "omni_scitune_instruction",
    "omni_charthal_evaluation",
    "omni_afenet_mcd",
    "omni_stabled_grounding_sam",
    "omni_odin_swarm_classification",
    "omni_html_omics_trust",
    "omni_ensemble_integration",
    "omni_mssvdd_subspace",
    "omni_implicit_vkood",
    "omni_gdb_benchmark",
    "omni_video_rm"
]

# Multimodal interface layer allowance mapping
allow {
    input.layer == "interface"
    valid_interface_engines[_] == input.engine_id
}

valid_interface_engines = [
    "omni_give_claude_eyes",
    "omni_clawdrive",
    "omni_speraxos_mcp_agent",
    "omni_mm_llms_sys_survey",
    "omni_dkn_reward"
]

# Deny fallback simulation or dummy execution logic explicitly
deny[msg] {
    input.features[_] == "simulation_override"
    msg := "OMNI production error: Overriding mathematical logic with simulation is strictly forbidden."
}

package omni.instruction.tuning

default allow = false

# Ensure instruction tuning datasets conform to strict length and safety rules
allow {
    input.dataset_name != ""
    input.prompt_length <= 4096
    input.has_human_feedback == true
}

deny[msg] {
    input.prompt_length > 4096
    msg := "Prompt length exceeds context window bounds"
}

deny[msg] {
    input.has_human_feedback == false
    msg := "Dataset lacks necessary RLHF alignment"
}

package rules.peft

default is_rank_valid = false

is_rank_valid {
    input.lora_rank > 0
    input.lora_rank <= input.max_allowed_rank
    # Rego policy ensuring LoRA rank conforms to hardware memory limits
}

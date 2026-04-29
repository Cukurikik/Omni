package rules.treelora

default keep_node = true

keep_node = false {
    input.gradient_similarity < 0.15
    # Rego policy defining structural pruning thresholds for TreeLoRA continuous learning
}

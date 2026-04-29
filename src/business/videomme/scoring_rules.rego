package rules.videomme

default is_valid_score = false

is_valid_score {
    input.score >= 0
    input.score <= 100
    input.has_reasoning_trace == true
    # Rego policy defining valid scoring bounds for Video-MME benchmark submissions
}

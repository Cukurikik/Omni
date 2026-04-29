package omni.semester14.batch8.clot

# OMNI Rego Policy for CLoT Humor Content
# Enforces strict content filtering on generated jokes

default allow_humor_generation = false

# Blacklisted categories
banned_topics := {"violence", "hate_speech", "nsfw", "politics"}

allow_humor_generation {
    input.request_type == "generate"
    input.tensor_mean > 0.0
    input.tensor_mean < 1.0
    
    # Ensure no banned topics are present
    count({x | x := input.topics[_]; banned_topics[x]}) == 0
}

deny[msg] {
    count({x | x := input.topics[_]; banned_topics[x]}) > 0
    msg := "OMNI_POLICY_ERR: Request contains banned topics."
}

deny[msg] {
    input.tensor_mean <= 0.0
    msg := "OMNI_POLICY_ERR: Invalid tensor mean."
}

package rules.aisearch

default boost_multiplier = 1.0

boost_multiplier = 1.5 {
    input.user_history_match == true
    input.document_freshness == "recent"
    # Rego policy to dynamically adjust search ranking boosts based on context
}

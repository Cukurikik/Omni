package rules.upgini

default is_data_safe = false

is_data_safe {
    input.contains_pii == false
    input.source_compliance == "GDPR"
    # Rego policy ensuring external features fetched by Upgini do not violate privacy
}

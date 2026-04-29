# Omni MLSecOps CTF Policy (Rego/OPA)
# Ref: alexdevassy/Machine_Learning_CTF_Challenges
package omni.mlctf_policy
default allow_model_query = false
allow_model_query {
    input.query_budget > 0
    input.query_budget <= 1000
    input.perturbation_epsilon <= 0.1
    not input.is_production_model
}
deny_extraction[msg] {
    input.query_budget > 1000
    msg := "Query budget exceeds limit for model extraction defense"
}
deny_adversarial[msg] {
    input.perturbation_epsilon > 0.1
    msg := "Perturbation epsilon too large for adversarial robustness"
}

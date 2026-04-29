package omni.security.cleverhans

default allow_adversarial_testing = false

allow_adversarial_testing {
    input.environment == "staging"
    input.role == "security_engineer"
}

deny_production_attack {
    input.environment == "production"
    input.attack_type != "none"
}

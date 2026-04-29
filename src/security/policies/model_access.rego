package omni.mlops

default allow_deploy = false

allow_deploy {
    input.user.role == "ml_engineer"
    input.model.passed_tests == true
}

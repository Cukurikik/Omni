package omni.security.jetson

# OMNI Rego Security Layer: NVIDIA Jetson Container Deployment
# Assures that ML containers pushed to Edge IoT devices are secure and signed.

default deploy_allowed = false

# Require verified NVIDIA L4T base images
valid_base_image {
    contains(input.image.repository, "nvcr.io/nvidia/l4t-pytorch")
}

valid_base_image {
    contains(input.image.repository, "nvcr.io/nvidia/l4t-ml")
}

# Require images to be signed by OMNI CI/CD pipeline
signed_by_omni {
    input.image.signature.issuer == "omni-security-nexus"
    input.image.signature.is_valid == true
}

# Allow deployment if valid and signed
deploy_allowed {
    valid_base_image
    signed_by_omni
    input.device.architecture == "aarch64"
    input.device.cuda_cores > 0
}

# Deny containers requiring privileged root access (IoT security)
deny[msg] {
    input.pod_security_context.privileged == true
    msg = "Security Violation: Edge containers on Jetson cannot run in privileged mode."
}

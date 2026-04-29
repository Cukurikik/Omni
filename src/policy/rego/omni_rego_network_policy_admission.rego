# OMNI MOTHER — SEMESTER 13 REMEDIATION
# Rego Language — Security & Policy Layer (OMNI Zero-Mock Implementation)
# Implements Kubernetes Admission Controller network policy evaluation.
# Absorbs patterns from: github.com/open-policy-agent/gatekeeper

package omni.policy.k8s.admission

# Deny pods that don't have resource limits set
deny_missing_limits[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.resources.limits
    msg := sprintf("Container '%v' must have resource limits defined.", [container.name])
}

# Deny pods with privileged security context
deny_privileged[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged == true
    msg := sprintf("Container '%v' must not run as privileged.", [container.name])
}

# Deny pods without readiness probes for production namespaces
deny_missing_probes[msg] {
    input.request.kind.kind == "Pod"
    input.request.object.metadata.namespace == "production"
    container := input.request.object.spec.containers[_]
    not container.readinessProbe
    msg := sprintf("Container '%v' in production must have a readiness probe.", [container.name])
}

# Deny images from untrusted registries
deny_untrusted_registry[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not startswith(container.image, "gcr.io/")
    not startswith(container.image, "docker.io/library/")
    not startswith(container.image, "registry.internal.com/")
    msg := sprintf("Container '%v' uses untrusted registry: %v", [container.name, container.image])
}

# Deny host network access
deny_host_network[msg] {
    input.request.kind.kind == "Pod"
    input.request.object.spec.hostNetwork == true
    msg := "Pod must not use host network."
}

# Aggregate all denials for admission response
violations[msg] {
    deny_missing_limits[msg]
}
violations[msg] {
    deny_privileged[msg]
}
violations[msg] {
    deny_missing_probes[msg]
}
violations[msg] {
    deny_untrusted_registry[msg]
}
violations[msg] {
    deny_host_network[msg]
}

# Final admission decision
admission_response := {
    "allowed": count(violations) == 0,
    "violations": violations,
    "violation_count": count(violations),
}

# Omni GPTLens Audit Policy (Rego/OPA)
# Ref: git-disl/GPTLens
package omni.gptlens_audit
default allow_deploy = false
allow_deploy {
    input.verified_vulns == 0
    input.false_positive_rate < 0.5
}
high_risk[msg] {
    input.verified_vulns > 0
    some v in input.findings
    v.type == "reentrancy"
    msg := sprintf("BLOCK: Reentrancy at line %v", [v.line])
}

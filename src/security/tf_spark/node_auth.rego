package omni.security.tf_spark

# OMNI TF-SPARK: Node Authentication Policy
# Rego rules to authenticate and authorize Spark executor nodes attempting to join the TensorFlow distributed cluster.
# Source: yahoo/TensorFlowOnSpark

default node_authorized = false

# A node is authorized if it presents a valid cluster token and originates from an allowed VPC subnet
node_authorized {
    valid_cluster_token
    valid_subnet
}

valid_cluster_token {
    input.request_token == input.expected_cluster_token
}

valid_subnet {
    # Check if the node IP is within the allowed Spark VPC CIDR
    net.cidr_contains("10.0.0.0/16", input.node_ip)
}

# Deny nodes trying to join as Parameter Servers if they don't have the explicit PS label
deny[msg] {
    input.requested_role == "PS"
    not input.node_labels["allow_ps"] == "true"
    msg := "Node rejected: Lacks 'allow_ps' label required to operate as a Parameter Server."
}

# OMNI Framework - HashiCorp Vault Policy for AI Model Keys
# Regulates access to external API keys and internal signing keys

path "omni/secret/data/nlp/indictrans/*" {
  capabilities = ["read", "list"]
}

path "omni/secret/data/vision/dinov2/*" {
  capabilities = ["read"]
}

# Only CI/CD systems and admins can update keys
path "omni/secret/data/*" {
  capabilities = ["create", "update", "delete"]
  denied_parameters = {
    "foo" = ["bar"]
  }
}

# Allow systems to generate temporary STS tokens
path "omni/sts/generate" {
  capabilities = ["update"]
}

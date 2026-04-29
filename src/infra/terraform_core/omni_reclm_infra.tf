# Omni RecLM Infra (Terraform)
# Ref: HKUDS/RecLM — ACL2025
resource "aws_sagemaker_endpoint_configuration" "omni_reclm" {
  name = "omni-reclm-endpoint"
  production_variants {
    variant_name           = "primary"
    model_name             = "omni-reclm-model"
    initial_instance_count = 1
    instance_type          = "ml.g5.xlarge"
  }
  tags = { Project = "OMNI", Batch = "22", Engine = "RecLM" }
}

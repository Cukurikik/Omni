# Omni FusionBench GPU Cluster Infra (Terraform)
# Ref: tanganke/fusion_bench — MIT
resource "aws_sagemaker_notebook_instance" "omni_fusionbench" {
  name          = "omni-fusionbench-merge"
  role_arn      = "arn:aws:iam::role/SageMakerRole"
  instance_type = "ml.g5.4xlarge"
  tags = { Project = "OMNI", Batch = "23", Engine = "FusionBench" }
}
resource "aws_s3_bucket" "omni_fusionbench_models" {
  bucket = "omni-fusionbench-model-store"
  tags = { Project = "OMNI", Engine = "FusionBench" }
}

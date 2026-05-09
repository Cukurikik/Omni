# OMNI Infrastructure — GPU Provisioner
provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_node_group" "omni_gpu_cluster" {
  cluster_name    = "omni-production-cluster"
  node_group_name = "omni-a100-nodes"
  node_role_arn   = aws_iam_role.node_role.arn
  subnet_ids      = ["subnet-abcde012", "subnet-bcde012a"]

  scaling_config {
    desired_size = 2
    max_size     = 10
    min_size     = 1
  }

  instance_types = ["p4d.24xlarge"] # NVIDIA A100

  tags = {
    Environment = "Production"
    Layer       = "OMNI-Inference"
  }
}

# OMNI Infrastructure Layer: AWS Elastic Kubernetes Service (EKS)
# Terraform module to provision the distributed Omni Cluster capable of running Unikernels and Containers.

provider "aws" {
  region = "us-west-2"
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "all" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

module "omni_eks_cluster" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "omni-production-cluster"
  cluster_version = "1.28"

  vpc_id     = data.aws_vpc.default.id
  subnet_ids = data.aws_subnets.all.ids

  cluster_endpoint_public_access = true

  # Managed Node Groups tailored for heterogeneous AI loads
  eks_managed_node_groups = {
    # System & Control nodes
    omni_control_plane = {
      instance_types = ["t3.large"]
      min_size       = 2
      max_size       = 4
      desired_size   = 2
    }

    # Heavy GPU Inference Nodes
    omni_gpu_inference = {
      instance_types = ["g5.12xlarge"] # A10G GPUs
      min_size       = 1
      max_size       = 10
      desired_size   = 2
      
      taints = [{
        key    = "nvidia.com/gpu"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }

  tags = {
    Environment = "production"
    System      = "OMNI_FRAMEWORK"
  }
}

output "cluster_endpoint" {
  description = "Endpoint for the OMNI EKS control plane."
  value       = module.omni_eks_cluster.cluster_endpoint
}

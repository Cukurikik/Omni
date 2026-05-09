# OMNI Framework - MoE GPU Cluster (Terraform)
# Defines infrastructure for a massive multi-node training and inference cluster.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

# EFA (Elastic Fabric Adapter) is required for fast UCCL/NCCL P2P communications
resource "aws_placement_group" "omni_efa_pg" {
  name     = "omni-moe-efa-placement"
  strategy = "cluster"
}

# The main inference nodes (e.g. 8x H100)
resource "aws_instance" "omni_moe_h100_node" {
  count         = 8
  ami           = "ami-04f12eb62a1c61858" # Deep Learning OSS Nvidia Driver AMI
  instance_type = "p5.48xlarge"           # 8x H100 GPU Instance

  placement_group = aws_placement_group.omni_efa_pg.id

  # Network Interface for EFA
  network_interface {
    network_interface_id = aws_network_interface.efa_ni[count.index].id
    device_index         = 0
  }

  root_block_device {
    volume_size = 500
    volume_type = "gp3"
  }

  tags = {
    Name    = "omni-moe-worker-${count.index}"
    Project = "OMNI-Foundation"
    Role    = "Inference-Worker"
  }
}

resource "aws_network_interface" "efa_ni" {
  count     = 8
  subnet_id = aws_subnet.moe_subnet.id

  # Enables OS bypass for UCCL
  interface_type = "efa"
}

resource "aws_subnet" "moe_subnet" {
  vpc_id            = aws_vpc.moe_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
}

resource "aws_vpc" "moe_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
}

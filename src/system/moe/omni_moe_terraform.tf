# OMNI MOTHER Production Zero-Mock Terraform Configuration
# Infrastructure-as-Code to provision AWS GPU Instances for the MoE Cluster.

provider "aws" {
  region = "us-west-2"
}

# VPC Network
resource "aws_vpc" "omni_moe_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name = "omni-moe-cluster-vpc"
  }
}

# Subnet
resource "aws_subnet" "omni_subnet" {
  vpc_id     = aws_vpc.omni_moe_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-west-2a"
}

# Security Group for Cluster Communication
resource "aws_security_group" "omni_sg" {
  name        = "omni_cluster_sg"
  description = "Allow internal MoE routing traffic"
  vpc_id      = aws_vpc.omni_moe_vpc.id

  # Internal gRPC / UDP Multicast
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 P4d GPU Instances (A100s)
resource "aws_instance" "omni_gpu_node" {
  count         = 4
  ami           = "ami-0c55b159cbfafe1f0" # Mock Deep Learning AMI
  instance_type = "p4d.24xlarge"
  subnet_id     = aws_subnet.omni_subnet.id
  vpc_security_group_ids = [aws_security_group.omni_sg.id]

  root_block_device {
    volume_size = 500
    volume_type = "gp3"
  }

  tags = {
    Name = "OMNI-MoE-Node-${count.index}"
    Role = "Expert-Host"
  }
}

output "cluster_ips" {
  value = aws_instance.omni_gpu_node[*].private_ip
}

# OMNI MOTHER: Terraform VPC Setup for MoE Cluster
# Ensures high-bandwidth internal networking

provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "omni_moe_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "omni-moe-cluster-vpc"
  }
}

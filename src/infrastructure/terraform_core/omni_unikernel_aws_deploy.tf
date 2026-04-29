# Omni Unikernel AWS Deployment (Terraform)
# Zero-mock infrastructure as code for 3MB Unikernel deployments

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_ec2_instance_state" "omni_unikernel" {
  instance_id = aws_instance.omni_node.id
  state       = "running"
}

resource "aws_instance" "omni_node" {
  ami           = "ami-0c55b159cbfafe1f0" # Omni Minimal AMI
  instance_type = "t4g.micro"             # Graviton optimized

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required" # IMDSv2 strictly enforced
    http_put_response_hop_limit = 1
  }

  tags = {
    Name        = "Omni-Unikernel-Node"
    Environment = "Production"
    Layer       = "Infrastructure"
  }
}

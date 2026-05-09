# OMNI MOTHER: Terraform Infrastructure Layer
# Provisions GPU instances for the PiKV Cache and MoE Experts

provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "omni_moe_expert" {
  count         = 8
  ami           = "ami-0abcdef1234567890" # Mock Deep Learning AMI
  instance_type = "p4d.24xlarge" # 8x A100

  tags = {
    Name = "omni-expert-${count.index}"
    Role = "moe-worker"
  }
}

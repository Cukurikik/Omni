# Omni LLM-Drop Infra (Terraform)
# Infrastructure Layer: Immutable provisioning of cluster nodes for layer dropping experiments.

provider "aws" {
  region = "us-east-1"
}

resource "aws_autoscaling_group" "omni_llmdrop_asg" {
  name                 = "omni-llmdrop-asg"
  max_size             = 10
  min_size             = 1
  desired_capacity     = 3
  vpc_zone_identifier  = ["subnet-abcde012", "subnet-bcde012a"]
  
  launch_template {
    id      = "lt-0a1b2c3d4e5f6g7h8" # Omni Base Template
    version = "$Latest"
  }

  tag {
    key                 = "OmniLayer"
    value               = "LLM-Drop"
    propagate_at_launch = true
  }
}

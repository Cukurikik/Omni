# OMNI MOTHER: Infrastructure as Code (Production Grade)
# Deploys the Omni Cloud Unikernel Cluster on AWS.

provider "aws" {
  region = "us-west-2"
}

resource "aws_autoscaling_group" "omni_cluster" {
  name                 = "omni-unikernel-asg"
  max_size             = 1000
  min_size             = 10
  desired_capacity     = 50
  vpc_zone_identifier  = ["subnet-123456"]

  launch_template {
    id      = aws_launch_template.omni_node.id
    version = "$Latest"
  }
}

resource "aws_launch_template" "omni_node" {
  name_prefix   = "omni-node-"
  image_id      = "ami-mockunikernel"
  instance_type = "g5.4xlarge" # GPU instance

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "OmniMoE-ComputeNode"
    }
  }
}

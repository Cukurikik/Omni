# OMNI Framework - Auto-Scaling Group (Terraform)
# Provisions an AWS Auto-Scaling Group to dynamically spin up 
# g5.12xlarge instances (4x A10G) based on MoE router utilization.

resource "aws_launch_template" "omni_moe_node" {
  name_prefix   = "omni-moe-node-"
  image_id      = "ami-0c55b159cbfafe1f0" # Ubuntu Deep Learning AMI
  instance_type = "g5.12xlarge"

  user_data = base64encode(<<EOF
#!/bin/bash
echo "OMNI AutoScale: Node Initializing..."
/opt/omni/bin/omni_llm_server_launcher &
EOF
  )
}

resource "aws_autoscaling_group" "omni_moe_asg" {
  desired_capacity    = 2
  max_size           = 10
  min_size           = 1
  vpc_zone_identifier = ["subnet-12345678"]

  launch_template {
    id      = aws_launch_template.omni_moe_node.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "Omni-MoE-GPU-Node"
    propagate_at_launch = true
  }
}

# OMNI MOTHER: Terraform Load Balancer for gRPC Gateway
provider "aws" {
  region = "us-east-1"
}

resource "aws_lb" "omni_grpc_lb" {
  name               = "omni-grpc-gateway-lb"
  internal           = false
  load_balancer_type = "network"
  subnets            = ["subnet-abcdef01"]

  tags = {
    Environment = "production"
  }
}

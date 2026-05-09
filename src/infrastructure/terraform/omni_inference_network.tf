# OMNI Infrastructure — Terraform GPU Inference Network
# VPC, subnets, security groups for GPU inference cluster.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = { source = "hashicorp/aws"; version = "~> 5.0" }
  }
}

variable "region" { default = "us-east-1" }
variable "cluster_name" { default = "omni-inference" }
variable "gpu_instance_type" { default = "g5.2xlarge" }
variable "min_nodes" { default = 1 }
variable "max_nodes" { default = 10 }
variable "desired_nodes" { default = 3 }

provider "aws" { region = var.region }

resource "aws_vpc" "inference" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "${var.cluster_name}-vpc" }
}

resource "aws_subnet" "gpu_a" {
  vpc_id            = aws_vpc.inference.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.region}a"
  map_public_ip_on_launch = true
  tags = { Name = "${var.cluster_name}-gpu-a" }
}

resource "aws_subnet" "gpu_b" {
  vpc_id            = aws_vpc.inference.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.region}b"
  map_public_ip_on_launch = true
  tags = { Name = "${var.cluster_name}-gpu-b" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.inference.id
  tags   = { Name = "${var.cluster_name}-igw" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.inference.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "gpu_a" {
  subnet_id      = aws_subnet.gpu_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "gpu_b" {
  subnet_id      = aws_subnet.gpu_b.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "inference" {
  name_prefix = "${var.cluster_name}-sg"
  vpc_id      = aws_vpc.inference.id

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
    description = "HTTP inference API"
  }

  ingress {
    from_port   = 50051
    to_port     = 50051
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
    description = "gRPC inference API"
  }

  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
    description = "Prometheus metrics"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.cluster_name}-sg" }
}

resource "aws_launch_template" "gpu_node" {
  name_prefix   = "${var.cluster_name}-gpu-"
  instance_type = var.gpu_instance_type
  image_id      = "ami-0abcdef1234567890"

  network_interfaces {
    security_groups = [aws_security_group.inference.id]
  }

  block_device_mappings {
    device_name = "/dev/sda1"
    ebs { volume_size = 200; volume_type = "gp3"; iops = 6000 }
  }

  tag_specifications {
    resource_type = "instance"
    tags = { Name = "${var.cluster_name}-gpu-node", Role = "inference" }
  }
}

resource "aws_autoscaling_group" "gpu" {
  name                = "${var.cluster_name}-gpu-asg"
  min_size            = var.min_nodes
  max_size            = var.max_nodes
  desired_capacity    = var.desired_nodes
  vpc_zone_identifier = [aws_subnet.gpu_a.id, aws_subnet.gpu_b.id]

  launch_template {
    id      = aws_launch_template.gpu_node.id
    version = "$Latest"
  }

  tag {
    key                 = "Cluster"
    value               = var.cluster_name
    propagate_at_launch = true
  }
}

output "vpc_id" { value = aws_vpc.inference.id }
output "subnet_ids" { value = [aws_subnet.gpu_a.id, aws_subnet.gpu_b.id] }
output "security_group_id" { value = aws_security_group.inference.id }

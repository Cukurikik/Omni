# @omni-layer Infrastructure | @omni-lang Terraform | @omni-batch 18 | @omni-semester 16
# @omni-description Terraform IaC for transformer inference cluster:
# GPU instances, load balancer, auto-scaling, model registry S3 bucket.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws"; version = "~> 5.0" }
  }
}

variable "cluster_name" { default = "omni-transformer-cluster" }
variable "region"       { default = "us-east-1" }
variable "gpu_instance" { default = "g5.xlarge" }
variable "min_nodes"    { default = 2 }
variable "max_nodes"    { default = 20 }
variable "model_bucket" { default = "omni-transformer-models" }

provider "aws" { region = var.region }

resource "aws_s3_bucket" "model_registry" {
  bucket = var.model_bucket
  tags   = { Project = "OMNI", Layer = "compute", Batch = "18" }
}

resource "aws_s3_bucket_versioning" "model_versioning" {
  bucket = aws_s3_bucket.model_registry.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_ecs_cluster" "transformer" {
  name = var.cluster_name
  setting { name = "containerInsights"; value = "enabled" }
}

resource "aws_ecs_task_definition" "inference" {
  family                   = "omni-transformer-inference"
  network_mode             = "awsvpc"
  requires_compatibilities = ["EC2"]
  cpu                      = "4096"
  memory                   = "16384"

  container_definitions = jsonencode([{
    name      = "transformer-inference"
    image     = "omni/transformer-inference:latest"
    cpu       = 4096
    memory    = 16384
    essential = true
    portMappings = [{ containerPort = 8080, protocol = "tcp" }]
    environment = [
      { name = "MODEL_BUCKET", value = var.model_bucket },
      { name = "MAX_BATCH_SIZE", value = "32" },
      { name = "DEVICE", value = "cuda" },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options   = { "awslogs-group" = "/ecs/omni-transformer", "awslogs-region" = var.region }
    }
  }])
}

resource "aws_appautoscaling_target" "inference_scaling" {
  max_capacity       = var.max_nodes
  min_capacity       = var.min_nodes
  resource_id        = "service/${aws_ecs_cluster.transformer.name}/omni-inference"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "gpu_scaling" {
  name               = "gpu-utilization-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.inference_scaling.resource_id
  scalable_dimension = aws_appautoscaling_target.inference_scaling.scalable_dimension
  service_namespace  = aws_appautoscaling_target.inference_scaling.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

resource "aws_lb" "inference_lb" {
  name               = "omni-transformer-lb"
  internal           = false
  load_balancer_type = "application"
  tags               = { Project = "OMNI", Layer = "infrastructure" }
}

output "cluster_name"     { value = aws_ecs_cluster.transformer.name }
output "model_bucket_arn" { value = aws_s3_bucket.model_registry.arn }
output "lb_dns"           { value = aws_lb.inference_lb.dns_name }

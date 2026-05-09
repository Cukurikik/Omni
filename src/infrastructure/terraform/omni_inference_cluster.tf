# OMNI Infrastructure Layer — Terraform for Model Serving
# GPU inference cluster on AWS with auto-scaling.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws"; version = "~> 5.0" }
  }
}

variable "model_name"   { type = string; default = "omni-7b" }
variable "region"       { type = string; default = "us-east-1" }
variable "gpu_instance" { type = string; default = "g5.xlarge" }
variable "min_capacity" { type = number; default = 1 }
variable "max_capacity" { type = number; default = 10 }

provider "aws" { region = var.region }

resource "aws_ecs_cluster" "inference" {
  name = "${var.model_name}-cluster"
  setting { name = "containerInsights"; value = "enabled" }
}

resource "aws_ecs_task_definition" "inference" {
  family                   = "${var.model_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["EC2"]
  cpu                      = "4096"
  memory                   = "16384"

  container_definitions = jsonencode([{
    name  = "inference"
    image = "omni-registry/${var.model_name}:latest"
    portMappings = [{ containerPort = 8080, protocol = "tcp" }]
    resourceRequirements = [{ type = "GPU", value = "1" }]
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8081/health || exit 1"]
      interval    = 30
      timeout     = 10
      retries     = 3
      startPeriod = 120
    }
    logConfiguration = {
      logDriver = "awslogs"
      options   = { "awslogs-group" = "/ecs/${var.model_name}", "awslogs-region" = var.region }
    }
  }])
}

resource "aws_appautoscaling_target" "inference" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.inference.name}/${var.model_name}-svc"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "${var.model_name}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.inference.resource_id
  scalable_dimension = aws_appautoscaling_target.inference.scalable_dimension
  service_namespace  = aws_appautoscaling_target.inference.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70.0
    predefined_metric_specification { predefined_metric_type = "ECSServiceAverageCPUUtilization" }
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

output "cluster_arn" { value = aws_ecs_cluster.inference.arn }
output "task_arn"    { value = aws_ecs_task_definition.inference.arn }

# @omni-layer Infrastructure | @omni-lang Terraform (HCL) | @omni-batch 17
# @omni-description OMNI Cloud deployment: Terraform module for provisioning
# GPU inference cluster with auto-scaling, load balancer, and model storage.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

variable "cluster_name"     { type = string; default = "omni-inference" }
variable "region"           { type = string; default = "us-east-1" }
variable "gpu_instance_type" { type = string; default = "g5.xlarge" }
variable "min_instances"    { type = number; default = 1 }
variable "max_instances"    { type = number; default = 10 }
variable "model_bucket"     { type = string; default = "omni-models-prod" }

resource "aws_s3_bucket" "model_store" {
  bucket = var.model_bucket
  tags = { Project = "OMNI", Layer = "Infrastructure", Batch = "17" }
}

resource "aws_s3_bucket_versioning" "model_versioning" {
  bucket = aws_s3_bucket.model_store.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_ecs_cluster" "inference_cluster" {
  name = var.cluster_name
  setting { name = "containerInsights"; value = "enabled" }
  tags = { Project = "OMNI", Component = "InferenceCluster" }
}

resource "aws_ecs_task_definition" "inference_task" {
  family                   = "${var.cluster_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "4096"
  memory                   = "16384"

  container_definitions = jsonencode([{
    name      = "omni-inference"
    image     = "omni/inference-server:latest"
    essential = true
    portMappings = [{ containerPort = 8080, protocol = "tcp" }]
    environment = [
      { name = "MODEL_BUCKET", value = var.model_bucket },
      { name = "MAX_BATCH_SIZE", value = "32" },
      { name = "DEVICE", value = "cuda" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/${var.cluster_name}"
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "inference"
      }
    }
  }])
}

resource "aws_lb" "inference_alb" {
  name               = "${var.cluster_name}-alb"
  internal           = false
  load_balancer_type = "application"
  tags = { Project = "OMNI" }
}

resource "aws_appautoscaling_target" "inference_scaling" {
  max_capacity       = var.max_instances
  min_capacity       = var.min_instances
  resource_id        = "service/${aws_ecs_cluster.inference_cluster.name}/${var.cluster_name}-svc"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "gpu_scaling" {
  name               = "${var.cluster_name}-gpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.inference_scaling.resource_id
  scalable_dimension = aws_appautoscaling_target.inference_scaling.scalable_dimension
  service_namespace  = aws_appautoscaling_target.inference_scaling.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 65.0
    scale_in_cooldown  = 120
    scale_out_cooldown = 60
  }
}

output "cluster_arn"   { value = aws_ecs_cluster.inference_cluster.arn }
output "model_bucket"  { value = aws_s3_bucket.model_store.bucket }
output "alb_dns"       { value = aws_lb.inference_alb.dns_name }

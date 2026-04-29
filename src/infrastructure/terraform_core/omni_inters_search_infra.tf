# Omni INTERS Search Infrastructure (Terraform)
# Zero-mock infrastructure as code for Elastic search clusters

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_elasticsearch_domain" "omni_inters_es" {
  domain_name           = "omni-inters-search"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r5.large.elasticsearch"
    instance_count = 3
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 100
  }

  tags = {
    Name        = "Omni-INTERS-Search-Cluster"
    Environment = "Production"
    Layer       = "Infrastructure"
  }
}

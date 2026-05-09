#=============================================================================
# OMNI INFRASTRUCTURE LAYER — OMNI CLOUD DEPLOYMENT (TERRAFORM)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Provisions Unikernel deployment infrastructure on AWS/GCP for 
#              the Omni AI modules (Transformers, ASR, Swarms).
#=============================================================================

terraform {
  required_providers {
    omnicloud = {
      source  = "omniframework/omnicloud"
      version = "~> 1.0.0"
    }
  }
}

provider "omnicloud" {
  region = "id-jkt-1"
}

# Define the High Performance Compute Cluster for Transformers
resource "omnicloud_unikernel_cluster" "ai_compute" {
  name        = "omni-ai-cluster"
  node_type   = "gpu-accelerated-v1"
  min_nodes   = 2
  max_nodes   = 50
  
  # Auto-scaling logic based on RAG and Vision model queue depths
  scaling_policy {
    metric = "queue_depth"
    target = 100
  }
}

# Deploy the compiled Omni Unikernel binary
resource "omnicloud_unikernel_deployment" "transformer_nexus" {
  cluster_id  = omnicloud_unikernel_cluster.ai_compute.id
  name        = "transformer-nexus"
  binary_path = "build/omni-ai-nexus.ukl" # Size: ~5MB 
  
  environment_variables = {
    OMNI_ENV      = "production"
    VECTOR_DB_URL = "qdrant://internal-cluster:6334"
  }
  
  network_acls = [
    "0.0.0.0/0:80",
    "0.0.0.0/0:443"
  ]
}

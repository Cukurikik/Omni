# OMNI Framework - Terraform Configuration for Ruformers Cluster
# Provisions scalable compute instances for Russian NLP processing

provider "google" {
  project = "omni-production"
  region  = "europe-west3" # Frankfurt region for latency
}

resource "google_compute_instance_group_manager" "ruformers_cluster" {
  name               = "omni-ruformers-igm"
  base_instance_name = "ruformers-node"
  zone               = "europe-west3-a"
  
  version {
    instance_template = google_compute_instance_template.ruformers_template.id
  }

  target_size = 3
}

resource "google_compute_instance_template" "ruformers_template" {
  name         = "omni-ruformers-template"
  machine_type = "n2-standard-8"

  disk {
    source_image = "omni-registry/ubuntu-2204-gpu-optimized"
    auto_delete  = true
    boot         = true
  }

  guest_accelerator {
    type  = "nvidia-tesla-t4"
    count = 1
  }

  network_interface {
    network = "default"
    access_config {
      # Ephemeral public IP
    }
  }

  metadata = {
    omni-role = "nlp-compute"
    model     = "ruformers"
  }
}

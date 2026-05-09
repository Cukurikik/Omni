# OMNI Infrastructure - TPU Provisioning for GHN3 Hypernetwork Training
provider "google" {
  project = var.gcp_project_id
  region  = "us-central1"
  zone    = "us-central1-a"
}

resource "google_tpu_node" "omni_ghn3_tpu" {
  name           = "omni-ghn3-hypernetwork"
  accelerator_type = "v3-8"
  tensorflow_version = "2.11.0"
  
  network = "default"
  
  labels = {
    framework = "omni"
    model     = "ghn3"
  }
}

output "tpu_ip" {
  value = google_tpu_node.omni_ghn3_tpu.network_endpoints[0].ip_address
}

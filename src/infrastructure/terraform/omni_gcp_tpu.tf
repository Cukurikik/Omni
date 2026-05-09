# OMNI Infrastructure — Terraform GCP TPU Provisioning

provider "google" {
  project = "omni-production-project"
  region  = "us-central1"
  zone    = "us-central1-b"
}

resource "google_tpu_v2_vm" "omni_tpu_node" {
  name = "omni-tpu-accelerator-1"
  zone = "us-central1-b"

  # Using TPU v4 for high-performance training
  accelerator_type = "v4-8"
  
  # Base image with TPU drivers pre-installed
  runtime_version = "tpu-ubuntu2204-base"

  network_config {
    network    = google_compute_network.omni_vpc.id
    subnetwork = google_compute_subnetwork.omni_subnet.id
  }

  labels = {
    environment = "production"
    layer       = "compute"
    framework   = "omni"
  }
}

resource "google_compute_network" "omni_vpc" {
  name                    = "omni-tpu-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "omni_subnet" {
  name          = "omni-tpu-subnet"
  ip_cidr_range = "10.2.0.0/16"
  region        = "us-central1"
  network       = google_compute_network.omni_vpc.id
}

# OMNI Infrastructure Layer
# Puppet manifest to ensure the physical GPU fleet is properly configured
# for the Omni Universal Binary. Installs drivers, CUDA toolkits, and fabric manager.

class omni_gpu_infrastructure (
  String $driver_version = '535.104.05',
  String $cuda_version = '12.2',
) {

  # Ensure the system is up to date before installing kernel modules
  exec { 'apt-update':
    command => '/usr/bin/apt-get update',
    refreshonly => true,
  }

  # Install essential build tools required for DKMS and Omni C++ compilation
  package { ['build-essential', 'dkms', 'linux-headers-generic']:
    ensure => installed,
    require => Exec['apt-update'],
  }

  # Add the official NVIDIA network repository for the specific OS
  exec { 'add-nvidia-repo':
    command => '/usr/bin/wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb && /usr/bin/dpkg -i cuda-keyring_1.1-1_all.deb && /usr/bin/apt-get update',
    creates => '/etc/apt/sources.list.d/cuda-ubuntu2204-x86_64.list',
  }

  # Install the specific headless driver required by Omni
  package { "nvidia-headless-${driver_version}":
    ensure  => installed,
    require => Exec['add-nvidia-repo'],
  }

  # Install the CUDA toolkit matching the Omni build matrix
  package { "cuda-toolkit-${cuda_version}":
    ensure  => installed,
    require => Package["nvidia-headless-${driver_version}"],
  }

  # Start and enable the NVIDIA Fabric Manager for multi-GPU NVLink (e.g., A100/H100)
  service { 'nvidia-fabricmanager':
    ensure    => running,
    enable    => true,
    require   => Package["cuda-toolkit-${cuda_version}"],
  }

  # Ensure persistence mode is on to prevent driver unloading, reducing inference latency
  exec { 'enable-persistence-mode':
    command => '/usr/bin/nvidia-smi -pm 1',
    unless  => '/usr/bin/nvidia-smi -q | grep -q "Persistence Mode.*Enabled"',
    require => Package["nvidia-headless-${driver_version}"],
  }

  notify { 'OMNI GPU Infrastructure Setup Complete.':
    require => Exec['enable-persistence-mode'],
  }
}

include omni_gpu_infrastructure

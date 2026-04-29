#!/bin/bash
# Omni Auffusion Bootstrap (Bash)
# System Layer: Deterministic startup sequence for the Auffusion audio generation engine.

set -euo pipefail

echo "[OMNI] Initializing Auffusion Engine..."

# Strict validation of CUDA environment
if ! command -v nvcc &> /dev/null; then
    echo "[OMNI_FATAL] CUDA compiler not found. Auffusion requires native GPU acceleration."
    exit 1
fi

export OMNI_AUDIO_LATENT_DIM=512
export OMNI_SAMPLE_RATE=48000
export OMNI_CHANNELS=2

echo "[OMNI] Auffusion bounds locked. Audio Latent Dim: $OMNI_AUDIO_LATENT_DIM"
echo "[OMNI] Engine Ready."
exit 0

#!/usr/bin/env bash
set -e

# Omni Docker/Unikernel Entrypoint (Bash)
# System & Infrastructure Layer
# Handles bootstrap initialization, environment verification,
# and zero-downtime execution of the Omni Universal Binary.

echo "[Omni Mother Nexus] Initializing Sub-Agents..."

# 1. Verify GPU availability (Zero-mock: check for nvidia-smi if available)
if command -v nvidia-smi &> /dev/null; then
    echo "[Info] NVIDIA GPU detected. Configuring CUDA visible devices."
    # Pin GPUs explicitly if defined
    export CUDA_VISIBLE_DEVICES=${OMNI_GPU_DEVICES:-"all"}
    nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
else
    echo "[Warn] No NVIDIA GPU detected. Falling back to AVX-512 CPU SIMD mode."
    export OMNI_EXECUTION_MODE="CPU_SIMD"
fi

# 2. Setup HugePages for memory-mapped KV Caches
if [ "$OMNI_ENABLE_HUGEPAGES" = "true" ]; then
    echo "[Info] Attempting to allocate HugePages for zero-copy memory operations."
    sysctl -w vm.nr_hugepages=1024 || echo "[Warn] Failed to allocate HugePages. Need root privileges."
fi

# 3. Secure Key Management Check
if [ -z "$OMNI_CLUSTER_SECRET" ]; then
    echo "[Fatal] OMNI_CLUSTER_SECRET is not set. Terminating node initialization."
    exit 1
fi

# 4. Execute the Universal Binary compiled by LLVM-Omni
echo "[Success] Environment verified. Launching Omni Universal Binary..."
exec /opt/omni/bin/omni_universal_binary \
    --config /etc/omni/Omnifile.toml \
    --log-level info \
    "$@"

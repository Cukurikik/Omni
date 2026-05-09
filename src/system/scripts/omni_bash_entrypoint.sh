#!/bin/bash
set -e

# OMNI System & Initialization Layer
# Bash entrypoint script for the Omni Docker container / Unikernel.
# Ensures zero-trust security bounds and proper environment initialization before
# yielding control to the native Universal Binary.

echo "[OMNI Entrypoint] Initializing Universal Environment..."

# 1. Read configuration from environment variables or fallbacks
OMNI_MODE="${OMNI_MODE:-production}"
OMNI_THREADS="${OMNI_THREADS:-auto}"
OMNI_BIND_ADDR="${OMNI_BIND_ADDR:-0.0.0.0}"

echo "[OMNI Entrypoint] Mode: $OMNI_MODE | Threads: $OMNI_THREADS"

# 2. System limits tuning for high-performance memory pinning
# Note: Requires container to run with --cap-add=IPC_LOCK in production
if ulimit -l unlimited 2>/dev/null; then
    echo "[OMNI Entrypoint] Memory pinning (mlock) enabled."
else
    echo "[OMNI Entrypoint] Warning: mlock failed. Zero-copy may fallback to standard memory mapping."
fi

# 3. Dynamic Hardware Discovery (e.g., CUDA, ROCm, AVX512)
if command -v nvidia-smi &> /dev/null; then
    echo "[OMNI Entrypoint] NVIDIA GPU detected. Native Tensor Core dispatch enabled."
    export OMNI_HARDWARE_TARGET="cuda"
else
    echo "[OMNI Entrypoint] No GPU detected. Defaulting to CPU AVX-512 backend."
    export OMNI_HARDWARE_TARGET="cpu_avx512"
fi

echo "[OMNI Entrypoint] Bootstrapping Universal Binary..."

# 4. Execute the main binary. We use 'exec' so the binary takes PID 1
# This ensures it receives Unix signals (SIGTERM, SIGINT) directly for graceful shutdown.
exec /bin/omni_entrypoint --mode="$OMNI_MODE" --threads="$OMNI_THREADS" --bind="$OMNI_BIND_ADDR"

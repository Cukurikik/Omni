#!/bin/bash
# OMNI Framework - MoE Development Environment Setup
# Initializes the multi-language workspace for developing the OMNI MoE Core.

echo "================================================="
echo "🪐 OMNI MOTHER - Polyglot MoE Dev Env Initializer"
echo "================================================="

# 1. Check for Conda
if ! command -v conda &> /dev/null; then
    echo "[ERROR] Conda not found. Please install Miniconda/Anaconda."
    exit 1
fi

ENV_NAME="omni-moe-dev"

# 2. Create or activate Conda environment
if conda info --envs | grep -q "$ENV_NAME"; then
    echo "[INFO] Conda environment '$ENV_NAME' already exists. Activating..."
else
    echo "[INFO] Creating Conda environment '$ENV_NAME' with Python 3.11..."
    conda create -y -n $ENV_NAME python=3.11
fi

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

# 3. Install Python DL Dependencies
echo "[INFO] Installing PyTorch and deep learning dependencies..."
pip install --quiet torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install --quiet transformers pytest faiss-cpu

# 4. Check for Go
if ! command -v go &> /dev/null; then
    echo "[WARNING] Go compiler not found. Network layers cannot be built."
else
    echo "[INFO] Go compiler found: $(go version)"
fi

# 5. Check for Rust
if ! command -v cargo &> /dev/null; then
    echo "[WARNING] Cargo not found. System allocators cannot be built."
else
    echo "[INFO] Rust compiler found: $(cargo --version)"
fi

echo "================================================="
echo "✅ Environment '$ENV_NAME' is ready for OMNI MoE development."
echo "Execute: conda activate $ENV_NAME"

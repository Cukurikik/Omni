# OMNI Framework - GPU Inference Worker Dockerfile
# Builds a production-ready container for PyTorch/CUDA-based transformer inference.

FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements-gpu.txt .
RUN pip3 install --no-cache-dir -r requirements-gpu.txt
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Copy the Omni Python inference layer
COPY src/compute/python/ /app/src/compute/python/

# Set the entrypoint to the inference server
CMD ["python3", "-m", "src.compute.python.omni_impruver_pretrain_pipeline"]

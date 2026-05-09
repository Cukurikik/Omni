#!/bin/bash

# OMNI MOTHER: Cluster Down Script
# Gracefully tears down the MoE ecosystem processes.

echo "[OMNI] Tearing down MoE Cluster..."

# Find and kill Go Router
echo "[OMNI] Terminating Router Gateway..."
pkill -f omni_router || echo "Router not running."

# Find and kill Expert Nodes
echo "[OMNI] Terminating Expert Nodes..."
pkill -f expert_node || echo "Experts not running."

# Clean up IPC/Shared memory if any
echo "[OMNI] Cleaning up CUDA IPC shared memory segments..."
rm -f /dev/shm/omni_cuda_ipc_* || true

echo "[OMNI] Cluster is DOWN."

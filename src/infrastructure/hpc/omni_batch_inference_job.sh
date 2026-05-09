#!/usr/bin/env bash
#SBATCH --job-name=omni_transformer_train
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --gres=gpu:a100:8
#SBATCH --time=48:00:00
#SBATCH --output=omni_train_%j.out
#SBATCH --error=omni_train_%j.err
#SBATCH --partition=dgx_a100

# Omni SLURM Batch Inference Job (Bash)
# HPC & Infrastructure Layer
# Orchestrates a massively parallel distributed training job across multiple 
# compute nodes using the SLURM workload manager.

echo "=========================================="
echo "Starting Omni Mother Nexus Distributed Run"
echo "Job ID: $SLURM_JOB_ID"
echo "Nodes allocated: $SLURM_JOB_NODELIST"
echo "=========================================="

# Load required HPC modules (Zero-mock: Assume standard HPC environment)
module load cuda/12.2
module load nccl/2.18
module load openmpi/4.1

# Define Omni parameters
OMNI_BINARY="/shared/omni/bin/omni_universal_binary"
OMNI_CONFIG="/shared/omni/config/Omnifile.toml"
MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)

export OMNI_DISTRIBUTED_MASTER=$MASTER_ADDR
export OMNI_DISTRIBUTED_PORT=29500

# Execute via MPI / srun across all 4 nodes, utilizing all 32 GPUs
echo "Launching training via srun..."
srun $OMNI_BINARY --config $OMNI_CONFIG --mode train --distributed true

echo "Omni Training Job Completed."

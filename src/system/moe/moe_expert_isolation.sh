#!/bin/bash
# moe_expert_isolation.sh — System / OS
# Layer: System / OS — Cgroup Resource Isolation
#
# Prevents a rogue or heavily loaded MoE worker process from starving the rest
# of the operating system (e.g., SSH, Network drivers) by enforcing strict
# Linux Control Group (cgroups) CPU and Memory limits.

set -e

CGROUP_NAME="omni_moe_workers"
MAX_MEMORY="128G"
# Allow using up to 24 cores (out of e.g. 32)
CPU_QUOTA=2400000 
CPU_PERIOD=100000

echo "[Cgroups] Enforcing Resource Isolation for MoE Workers..."

# Check if cgroups v2 is available
if [ -d "/sys/fs/cgroup" ]; then
    # Create the cgroup
    mkdir -p /sys/fs/cgroup/$CGROUP_NAME
    
    # Set Memory Limit
    echo $MAX_MEMORY > /sys/fs/cgroup/$CGROUP_NAME/memory.max
    
    # Set CPU Limit (Quota/Period)
    echo "$CPU_QUOTA $CPU_PERIOD" > /sys/fs/cgroup/$CGROUP_NAME/cpu.max
    
    echo "[Cgroups] Configured $CGROUP_NAME: Memory=$MAX_MEMORY, CPU=$CPU_QUOTA/$CPU_PERIOD"
else
    echo "[Cgroups] Error: /sys/fs/cgroup not found. Are you on Linux with Cgroups V2?"
    exit 1
fi

# Function to attach a PID to this cgroup
attach_pid() {
    local target_pid=$1
    echo $target_pid > /sys/fs/cgroup/$CGROUP_NAME/cgroup.procs
    echo "[Cgroups] Attached PID $target_pid to $CGROUP_NAME"
}

# In production, this script is sourced by the main init daemon
# attach_pid $$

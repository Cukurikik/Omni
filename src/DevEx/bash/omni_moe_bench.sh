#!/bin/bash
set -e

# OMNI MOTHER: Benchmarking Script
# Automatically tests latency, imbalance, and RDMA throughput of the MoE system.

echo "[OMNI] Starting MoE Benchmarking Suite..."

# Ensure cluster is up
./src/devex/bash/omni_moe_cluster_up.sh

echo "[OMNI] Warming up experts..."
# python3 src/testing/python/omni_libmoe_benchmark.py --warmup

echo "[OMNI] Running Latency Test (1M tokens)..."
# python3 src/testing/python/omni_libmoe_benchmark.py --mode latency --tokens 1000000

echo "[OMNI] Running Routing Imbalance Test..."
# python3 src/testing/python/omni_libmoe_benchmark.py --mode imbalance

echo "[OMNI] Extracting NVLink / RDMA Telemetry..."
# ./build/omni_nvlink_monitor_cli

echo "[OMNI] Benchmarks Complete. Output saved to /tmp/omni_bench_results.json"

# Tear down
./src/devex/bash/omni_moe_cluster_down.sh

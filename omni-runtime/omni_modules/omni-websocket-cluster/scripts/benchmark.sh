#!/bin/bash
# omni-websocket-cluster - Benchmark Script
set -e
echo 'Benchmarking omni-websocket-cluster...'
omni bench --module omni-websocket-cluster --iterations 10000
echo 'Benchmark complete.'
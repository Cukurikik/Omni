#!/bin/bash
# omni-tencent-cos - Benchmark Script
set -e
echo 'Benchmarking omni-tencent-cos...'
omni bench --module omni-tencent-cos --iterations 10000
echo 'Benchmark complete.'
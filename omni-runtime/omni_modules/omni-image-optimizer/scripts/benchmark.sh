#!/bin/bash
# omni-image-optimizer - Benchmark Script
set -e
echo 'Benchmarking omni-image-optimizer...'
omni bench --module omni-image-optimizer --iterations 10000
echo 'Benchmark complete.'
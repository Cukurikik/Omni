#!/bin/bash
# omni-backblaze-b2 - Benchmark Script
set -e
echo 'Benchmarking omni-backblaze-b2...'
omni bench --module omni-backblaze-b2 --iterations 10000
echo 'Benchmark complete.'
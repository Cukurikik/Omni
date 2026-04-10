#!/bin/bash
# omni-rive-animation - Benchmark Script
set -e
echo 'Benchmarking omni-rive-animation...'
omni bench --module omni-rive-animation --iterations 10000
echo 'Benchmark complete.'
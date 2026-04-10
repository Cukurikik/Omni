#!/bin/bash
# omni-canvas-turbo - Benchmark Script
set -e
echo 'Benchmarking omni-canvas-turbo...'
omni bench --module omni-canvas-turbo --iterations 10000
echo 'Benchmark complete.'
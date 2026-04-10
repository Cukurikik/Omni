#!/bin/bash
# omni-spline-3d - Benchmark Script
set -e
echo 'Benchmarking omni-spline-3d...'
omni bench --module omni-spline-3d --iterations 10000
echo 'Benchmark complete.'
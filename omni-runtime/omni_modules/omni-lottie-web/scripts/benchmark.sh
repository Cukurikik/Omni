#!/bin/bash
# omni-lottie-web - Benchmark Script
set -e
echo 'Benchmarking omni-lottie-web...'
omni bench --module omni-lottie-web --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-vercel-edge - Benchmark Script
set -e
echo 'Benchmarking omni-vercel-edge...'
omni bench --module omni-vercel-edge --iterations 10000
echo 'Benchmark complete.'
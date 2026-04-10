#!/bin/bash
# omni-netlify-edge - Benchmark Script
set -e
echo 'Benchmarking omni-netlify-edge...'
omni bench --module omni-netlify-edge --iterations 10000
echo 'Benchmark complete.'
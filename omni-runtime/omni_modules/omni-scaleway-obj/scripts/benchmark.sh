#!/bin/bash
# omni-scaleway-obj - Benchmark Script
set -e
echo 'Benchmarking omni-scaleway-obj...'
omni bench --module omni-scaleway-obj --iterations 10000
echo 'Benchmark complete.'
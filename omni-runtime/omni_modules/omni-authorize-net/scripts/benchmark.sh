#!/bin/bash
# omni-authorize-net - Benchmark Script
set -e
echo 'Benchmarking omni-authorize-net...'
omni bench --module omni-authorize-net --iterations 10000
echo 'Benchmark complete.'
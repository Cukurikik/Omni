#!/bin/bash
# omni-redis - Benchmark Script
set -e
echo 'Benchmarking omni-redis...'
omni bench --module omni-redis --iterations 10000
echo 'Benchmark complete.'
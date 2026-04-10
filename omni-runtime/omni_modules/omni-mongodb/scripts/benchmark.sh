#!/bin/bash
# omni-mongodb - Benchmark Script
set -e
echo 'Benchmarking omni-mongodb...'
omni bench --module omni-mongodb --iterations 10000
echo 'Benchmark complete.'
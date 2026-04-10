#!/bin/bash
# omni-mojs - Benchmark Script
set -e
echo 'Benchmarking omni-mojs...'
omni bench --module omni-mojs --iterations 10000
echo 'Benchmark complete.'
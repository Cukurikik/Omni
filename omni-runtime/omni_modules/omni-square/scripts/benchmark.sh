#!/bin/bash
# omni-square - Benchmark Script
set -e
echo 'Benchmarking omni-square...'
omni bench --module omni-square --iterations 10000
echo 'Benchmark complete.'
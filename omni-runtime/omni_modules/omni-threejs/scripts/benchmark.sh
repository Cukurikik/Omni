#!/bin/bash
# omni-threejs - Benchmark Script
set -e
echo 'Benchmarking omni-threejs...'
omni bench --module omni-threejs --iterations 10000
echo 'Benchmark complete.'
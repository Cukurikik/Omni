#!/bin/bash
# omni-webpack-killer - Benchmark Script
set -e
echo 'Benchmarking omni-webpack-killer...'
omni bench --module omni-webpack-killer --iterations 10000
echo 'Benchmark complete.'
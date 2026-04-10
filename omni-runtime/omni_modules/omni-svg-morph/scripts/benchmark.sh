#!/bin/bash
# omni-svg-morph - Benchmark Script
set -e
echo 'Benchmarking omni-svg-morph...'
omni bench --module omni-svg-morph --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-scrollreveal - Benchmark Script
set -e
echo 'Benchmarking omni-scrollreveal...'
omni bench --module omni-scrollreveal --iterations 10000
echo 'Benchmark complete.'
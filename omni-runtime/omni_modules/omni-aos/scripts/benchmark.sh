#!/bin/bash
# omni-aos - Benchmark Script
set -e
echo 'Benchmarking omni-aos...'
omni bench --module omni-aos --iterations 10000
echo 'Benchmark complete.'
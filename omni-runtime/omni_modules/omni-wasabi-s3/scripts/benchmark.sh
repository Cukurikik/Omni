#!/bin/bash
# omni-wasabi-s3 - Benchmark Script
set -e
echo 'Benchmarking omni-wasabi-s3...'
omni bench --module omni-wasabi-s3 --iterations 10000
echo 'Benchmark complete.'
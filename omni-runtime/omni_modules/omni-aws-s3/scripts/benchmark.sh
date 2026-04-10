#!/bin/bash
# omni-aws-s3 - Benchmark Script
set -e
echo 'Benchmarking omni-aws-s3...'
omni bench --module omni-aws-s3 --iterations 10000
echo 'Benchmark complete.'
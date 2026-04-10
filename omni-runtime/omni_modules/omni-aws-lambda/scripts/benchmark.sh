#!/bin/bash
# omni-aws-lambda - Benchmark Script
set -e
echo 'Benchmarking omni-aws-lambda...'
omni bench --module omni-aws-lambda --iterations 10000
echo 'Benchmark complete.'
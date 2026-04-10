#!/bin/bash
# omni-apple-pay - Benchmark Script
set -e
echo 'Benchmarking omni-apple-pay...'
omni bench --module omni-apple-pay --iterations 10000
echo 'Benchmark complete.'
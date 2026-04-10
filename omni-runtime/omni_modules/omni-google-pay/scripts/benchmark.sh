#!/bin/bash
# omni-google-pay - Benchmark Script
set -e
echo 'Benchmarking omni-google-pay...'
omni bench --module omni-google-pay --iterations 10000
echo 'Benchmark complete.'
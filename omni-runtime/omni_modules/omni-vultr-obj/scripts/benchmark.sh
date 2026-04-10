#!/bin/bash
# omni-vultr-obj - Benchmark Script
set -e
echo 'Benchmarking omni-vultr-obj...'
omni bench --module omni-vultr-obj --iterations 10000
echo 'Benchmark complete.'
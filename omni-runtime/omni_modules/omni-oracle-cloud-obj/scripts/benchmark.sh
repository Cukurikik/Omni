#!/bin/bash
# omni-oracle-cloud-obj - Benchmark Script
set -e
echo 'Benchmarking omni-oracle-cloud-obj...'
omni bench --module omni-oracle-cloud-obj --iterations 10000
echo 'Benchmark complete.'
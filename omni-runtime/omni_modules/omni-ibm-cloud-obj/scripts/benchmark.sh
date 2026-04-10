#!/bin/bash
# omni-ibm-cloud-obj - Benchmark Script
set -e
echo 'Benchmarking omni-ibm-cloud-obj...'
omni bench --module omni-ibm-cloud-obj --iterations 10000
echo 'Benchmark complete.'
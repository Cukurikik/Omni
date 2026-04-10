#!/bin/bash
# omni-linode-obj - Benchmark Script
set -e
echo 'Benchmarking omni-linode-obj...'
omni bench --module omni-linode-obj --iterations 10000
echo 'Benchmark complete.'
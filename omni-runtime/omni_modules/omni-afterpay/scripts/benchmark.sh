#!/bin/bash
# omni-afterpay - Benchmark Script
set -e
echo 'Benchmarking omni-afterpay...'
omni bench --module omni-afterpay --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-paystack - Benchmark Script
set -e
echo 'Benchmarking omni-paystack...'
omni bench --module omni-paystack --iterations 10000
echo 'Benchmark complete.'
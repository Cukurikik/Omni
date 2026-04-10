#!/bin/bash
# omni-coinbase-commerce - Benchmark Script
set -e
echo 'Benchmarking omni-coinbase-commerce...'
omni bench --module omni-coinbase-commerce --iterations 10000
echo 'Benchmark complete.'
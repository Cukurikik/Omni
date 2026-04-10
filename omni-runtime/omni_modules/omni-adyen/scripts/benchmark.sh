#!/bin/bash
# omni-adyen - Benchmark Script
set -e
echo 'Benchmarking omni-adyen...'
omni bench --module omni-adyen --iterations 10000
echo 'Benchmark complete.'
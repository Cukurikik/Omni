#!/bin/bash
# omni-bitpay - Benchmark Script
set -e
echo 'Benchmarking omni-bitpay...'
omni bench --module omni-bitpay --iterations 10000
echo 'Benchmark complete.'
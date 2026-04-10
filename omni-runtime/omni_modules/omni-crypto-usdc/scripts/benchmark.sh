#!/bin/bash
# omni-crypto-usdc - Benchmark Script
set -e
echo 'Benchmarking omni-crypto-usdc...'
omni bench --module omni-crypto-usdc --iterations 10000
echo 'Benchmark complete.'
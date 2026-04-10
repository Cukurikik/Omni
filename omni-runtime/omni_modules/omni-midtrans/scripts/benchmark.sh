#!/bin/bash
# omni-midtrans - Benchmark Script
set -e
echo 'Benchmarking omni-midtrans...'
omni bench --module omni-midtrans --iterations 10000
echo 'Benchmark complete.'
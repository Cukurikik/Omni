#!/bin/bash
# omni-klarna - Benchmark Script
set -e
echo 'Benchmarking omni-klarna...'
omni bench --module omni-klarna --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-mollie - Benchmark Script
set -e
echo 'Benchmarking omni-mollie...'
omni bench --module omni-mollie --iterations 10000
echo 'Benchmark complete.'
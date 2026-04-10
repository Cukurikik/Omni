#!/bin/bash
# omni-azure-functions - Benchmark Script
set -e
echo 'Benchmarking omni-azure-functions...'
omni bench --module omni-azure-functions --iterations 10000
echo 'Benchmark complete.'
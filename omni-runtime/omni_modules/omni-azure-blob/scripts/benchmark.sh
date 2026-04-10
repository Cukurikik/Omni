#!/bin/bash
# omni-azure-blob - Benchmark Script
set -e
echo 'Benchmarking omni-azure-blob...'
omni bench --module omni-azure-blob --iterations 10000
echo 'Benchmark complete.'
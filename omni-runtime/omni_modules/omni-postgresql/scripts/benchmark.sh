#!/bin/bash
# omni-postgresql - Benchmark Script
set -e
echo 'Benchmarking omni-postgresql...'
omni bench --module omni-postgresql --iterations 10000
echo 'Benchmark complete.'
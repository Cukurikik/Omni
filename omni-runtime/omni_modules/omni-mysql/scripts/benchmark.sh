#!/bin/bash
# omni-mysql - Benchmark Script
set -e
echo 'Benchmarking omni-mysql...'
omni bench --module omni-mysql --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-sqlite-turbo - Benchmark Script
set -e
echo 'Benchmarking omni-sqlite-turbo...'
omni bench --module omni-sqlite-turbo --iterations 10000
echo 'Benchmark complete.'
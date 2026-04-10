#!/bin/bash
# omni-typed-js - Benchmark Script
set -e
echo 'Benchmarking omni-typed-js...'
omni bench --module omni-typed-js --iterations 10000
echo 'Benchmark complete.'
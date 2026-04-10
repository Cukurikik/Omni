#!/bin/bash
# omni-wow-js - Benchmark Script
set -e
echo 'Benchmarking omni-wow-js...'
omni bench --module omni-wow-js --iterations 10000
echo 'Benchmark complete.'
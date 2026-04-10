#!/bin/bash
# omni-velocity-js - Benchmark Script
set -e
echo 'Benchmarking omni-velocity-js...'
omni bench --module omni-velocity-js --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-p5-js - Benchmark Script
set -e
echo 'Benchmarking omni-p5-js...'
omni bench --module omni-p5-js --iterations 10000
echo 'Benchmark complete.'
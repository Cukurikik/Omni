#!/bin/bash
# omni-matter-js - Benchmark Script
set -e
echo 'Benchmarking omni-matter-js...'
omni bench --module omni-matter-js --iterations 10000
echo 'Benchmark complete.'
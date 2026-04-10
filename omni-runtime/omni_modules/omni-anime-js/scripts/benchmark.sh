#!/bin/bash
# omni-anime-js - Benchmark Script
set -e
echo 'Benchmarking omni-anime-js...'
omni bench --module omni-anime-js --iterations 10000
echo 'Benchmark complete.'
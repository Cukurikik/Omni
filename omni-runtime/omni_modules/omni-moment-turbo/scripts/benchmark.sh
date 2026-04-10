#!/bin/bash
# omni-moment-turbo - Benchmark Script
set -e
echo 'Benchmarking omni-moment-turbo...'
omni bench --module omni-moment-turbo --iterations 10000
echo 'Benchmark complete.'
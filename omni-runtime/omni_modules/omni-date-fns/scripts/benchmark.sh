#!/bin/bash
# omni-date-fns - Benchmark Script
set -e
echo 'Benchmarking omni-date-fns...'
omni bench --module omni-date-fns --iterations 10000
echo 'Benchmark complete.'
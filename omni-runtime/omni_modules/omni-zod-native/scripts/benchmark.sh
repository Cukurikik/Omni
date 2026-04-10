#!/bin/bash
# omni-zod-native - Benchmark Script
set -e
echo 'Benchmarking omni-zod-native...'
omni bench --module omni-zod-native --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-prettier-native - Benchmark Script
set -e
echo 'Benchmarking omni-prettier-native...'
omni bench --module omni-prettier-native --iterations 10000
echo 'Benchmark complete.'
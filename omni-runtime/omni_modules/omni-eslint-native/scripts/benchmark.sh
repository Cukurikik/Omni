#!/bin/bash
# omni-eslint-native - Benchmark Script
set -e
echo 'Benchmarking omni-eslint-native...'
omni bench --module omni-eslint-native --iterations 10000
echo 'Benchmark complete.'
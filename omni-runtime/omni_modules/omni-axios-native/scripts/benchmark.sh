#!/bin/bash
# omni-axios-native - Benchmark Script
set -e
echo 'Benchmarking omni-axios-native...'
omni bench --module omni-axios-native --iterations 10000
echo 'Benchmark complete.'
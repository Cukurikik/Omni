#!/bin/bash
# omni-uuid-native - Benchmark Script
set -e
echo 'Benchmarking omni-uuid-native...'
omni bench --module omni-uuid-native --iterations 10000
echo 'Benchmark complete.'
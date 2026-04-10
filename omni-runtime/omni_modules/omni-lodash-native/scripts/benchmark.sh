#!/bin/bash
# omni-lodash-native - Benchmark Script
set -e
echo 'Benchmarking omni-lodash-native...'
omni bench --module omni-lodash-native --iterations 10000
echo 'Benchmark complete.'
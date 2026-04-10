#!/bin/bash
# omni-dynamodb-native - Benchmark Script
set -e
echo 'Benchmarking omni-dynamodb-native...'
omni bench --module omni-dynamodb-native --iterations 10000
echo 'Benchmark complete.'
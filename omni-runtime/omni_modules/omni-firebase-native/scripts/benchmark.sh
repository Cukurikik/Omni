#!/bin/bash
# omni-firebase-native - Benchmark Script
set -e
echo 'Benchmarking omni-firebase-native...'
omni bench --module omni-firebase-native --iterations 10000
echo 'Benchmark complete.'
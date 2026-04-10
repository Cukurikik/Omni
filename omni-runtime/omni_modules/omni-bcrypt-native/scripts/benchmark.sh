#!/bin/bash
# omni-bcrypt-native - Benchmark Script
set -e
echo 'Benchmarking omni-bcrypt-native...'
omni bench --module omni-bcrypt-native --iterations 10000
echo 'Benchmark complete.'
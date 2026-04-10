#!/bin/bash
# omni-socket-io-native - Benchmark Script
set -e
echo 'Benchmarking omni-socket-io-native...'
omni bench --module omni-socket-io-native --iterations 10000
echo 'Benchmark complete.'
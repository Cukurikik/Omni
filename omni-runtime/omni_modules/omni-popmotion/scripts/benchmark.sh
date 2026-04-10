#!/bin/bash
# omni-popmotion - Benchmark Script
set -e
echo 'Benchmarking omni-popmotion...'
omni bench --module omni-popmotion --iterations 10000
echo 'Benchmark complete.'
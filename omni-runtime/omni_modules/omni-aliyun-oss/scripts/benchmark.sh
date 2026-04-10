#!/bin/bash
# omni-aliyun-oss - Benchmark Script
set -e
echo 'Benchmarking omni-aliyun-oss...'
omni bench --module omni-aliyun-oss --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-wechat-pay - Benchmark Script
set -e
echo 'Benchmarking omni-wechat-pay...'
omni bench --module omni-wechat-pay --iterations 10000
echo 'Benchmark complete.'
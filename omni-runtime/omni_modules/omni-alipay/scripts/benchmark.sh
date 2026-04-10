#!/bin/bash
# omni-alipay - Benchmark Script
set -e
echo 'Benchmarking omni-alipay...'
omni bench --module omni-alipay --iterations 10000
echo 'Benchmark complete.'
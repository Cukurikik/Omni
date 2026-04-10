#!/bin/bash
# omni-xendit - Benchmark Script
set -e
echo 'Benchmarking omni-xendit...'
omni bench --module omni-xendit --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-elastic-search - Benchmark Script
set -e
echo 'Benchmarking omni-elastic-search...'
omni bench --module omni-elastic-search --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-cassandra - Benchmark Script
set -e
echo 'Benchmarking omni-cassandra...'
omni bench --module omni-cassandra --iterations 10000
echo 'Benchmark complete.'
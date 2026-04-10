#!/bin/bash
# omni-couchbase - Benchmark Script
set -e
echo 'Benchmarking omni-couchbase...'
omni bench --module omni-couchbase --iterations 10000
echo 'Benchmark complete.'
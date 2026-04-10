#!/bin/bash
# omni-weaviate - Benchmark Script
set -e
echo 'Benchmarking omni-weaviate...'
omni bench --module omni-weaviate --iterations 10000
echo 'Benchmark complete.'
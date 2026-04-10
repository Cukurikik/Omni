#!/bin/bash
# omni-milvus - Benchmark Script
set -e
echo 'Benchmarking omni-milvus...'
omni bench --module omni-milvus --iterations 10000
echo 'Benchmark complete.'
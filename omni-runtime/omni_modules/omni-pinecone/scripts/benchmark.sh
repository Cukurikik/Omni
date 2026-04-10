#!/bin/bash
# omni-pinecone - Benchmark Script
set -e
echo 'Benchmarking omni-pinecone...'
omni bench --module omni-pinecone --iterations 10000
echo 'Benchmark complete.'
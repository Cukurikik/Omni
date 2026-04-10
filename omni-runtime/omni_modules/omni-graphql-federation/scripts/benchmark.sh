#!/bin/bash
# omni-graphql-federation - Benchmark Script
set -e
echo 'Benchmarking omni-graphql-federation...'
omni bench --module omni-graphql-federation --iterations 10000
echo 'Benchmark complete.'
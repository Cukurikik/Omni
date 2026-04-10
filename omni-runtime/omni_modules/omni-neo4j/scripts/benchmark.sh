#!/bin/bash
# omni-neo4j - Benchmark Script
set -e
echo 'Benchmarking omni-neo4j...'
omni bench --module omni-neo4j --iterations 10000
echo 'Benchmark complete.'
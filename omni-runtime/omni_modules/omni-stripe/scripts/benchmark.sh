#!/bin/bash
# omni-stripe - Benchmark Script
set -e
echo 'Benchmarking omni-stripe...'
omni bench --module omni-stripe --iterations 10000
echo 'Benchmark complete.'
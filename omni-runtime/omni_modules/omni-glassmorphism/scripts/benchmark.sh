#!/bin/bash
# omni-glassmorphism - Benchmark Script
set -e
echo 'Benchmarking omni-glassmorphism...'
omni bench --module omni-glassmorphism --iterations 10000
echo 'Benchmark complete.'
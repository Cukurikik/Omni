#!/bin/bash
# omni-parallax-core - Benchmark Script
set -e
echo 'Benchmarking omni-parallax-core...'
omni bench --module omni-parallax-core --iterations 10000
echo 'Benchmark complete.'
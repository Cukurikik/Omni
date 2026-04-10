#!/bin/bash
# omni-gsap - Benchmark Script
set -e
echo 'Benchmarking omni-gsap...'
omni bench --module omni-gsap --iterations 10000
echo 'Benchmark complete.'
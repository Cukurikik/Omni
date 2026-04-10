#!/bin/bash
# omni-framer-motion - Benchmark Script
set -e
echo 'Benchmarking omni-framer-motion...'
omni bench --module omni-framer-motion --iterations 10000
echo 'Benchmark complete.'
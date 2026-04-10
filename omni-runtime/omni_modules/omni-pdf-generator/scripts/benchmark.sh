#!/bin/bash
# omni-pdf-generator - Benchmark Script
set -e
echo 'Benchmarking omni-pdf-generator...'
omni bench --module omni-pdf-generator --iterations 10000
echo 'Benchmark complete.'
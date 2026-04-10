#!/bin/bash
# omni-cloudflare-r2 - Benchmark Script
set -e
echo 'Benchmarking omni-cloudflare-r2...'
omni bench --module omni-cloudflare-r2 --iterations 10000
echo 'Benchmark complete.'
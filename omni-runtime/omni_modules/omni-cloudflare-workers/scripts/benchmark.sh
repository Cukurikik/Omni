#!/bin/bash
# omni-cloudflare-workers - Benchmark Script
set -e
echo 'Benchmarking omni-cloudflare-workers...'
omni bench --module omni-cloudflare-workers --iterations 10000
echo 'Benchmark complete.'
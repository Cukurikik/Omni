#!/bin/bash
# omni-cockroachdb - Benchmark Script
set -e
echo 'Benchmarking omni-cockroachdb...'
omni bench --module omni-cockroachdb --iterations 10000
echo 'Benchmark complete.'
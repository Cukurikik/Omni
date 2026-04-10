#!/bin/bash
# omni-timescaledb - Benchmark Script
set -e
echo 'Benchmarking omni-timescaledb...'
omni bench --module omni-timescaledb --iterations 10000
echo 'Benchmark complete.'
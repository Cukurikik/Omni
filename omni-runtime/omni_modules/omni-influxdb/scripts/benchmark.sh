#!/bin/bash
# omni-influxdb - Benchmark Script
set -e
echo 'Benchmarking omni-influxdb...'
omni bench --module omni-influxdb --iterations 10000
echo 'Benchmark complete.'
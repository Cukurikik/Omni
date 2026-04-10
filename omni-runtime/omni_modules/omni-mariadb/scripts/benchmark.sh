#!/bin/bash
# omni-mariadb - Benchmark Script
set -e
echo 'Benchmarking omni-mariadb...'
omni bench --module omni-mariadb --iterations 10000
echo 'Benchmark complete.'
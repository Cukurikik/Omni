#!/bin/bash
# omni-rabbitmq - Benchmark Script
set -e
echo 'Benchmarking omni-rabbitmq...'
omni bench --module omni-rabbitmq --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-kafka-stream - Benchmark Script
set -e
echo 'Benchmarking omni-kafka-stream...'
omni bench --module omni-kafka-stream --iterations 10000
echo 'Benchmark complete.'
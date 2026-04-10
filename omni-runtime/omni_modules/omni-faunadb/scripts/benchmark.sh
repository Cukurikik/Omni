#!/bin/bash
# omni-faunadb - Benchmark Script
set -e
echo 'Benchmarking omni-faunadb...'
omni bench --module omni-faunadb --iterations 10000
echo 'Benchmark complete.'
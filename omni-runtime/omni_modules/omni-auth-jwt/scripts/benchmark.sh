#!/bin/bash
# omni-auth-jwt - Benchmark Script
set -e
echo 'Benchmarking omni-auth-jwt...'
omni bench --module omni-auth-jwt --iterations 10000
echo 'Benchmark complete.'
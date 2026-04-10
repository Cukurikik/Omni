#!/bin/bash
# omni-braintree - Benchmark Script
set -e
echo 'Benchmarking omni-braintree...'
omni bench --module omni-braintree --iterations 10000
echo 'Benchmark complete.'
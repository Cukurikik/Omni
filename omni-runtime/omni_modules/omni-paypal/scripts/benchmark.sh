#!/bin/bash
# omni-paypal - Benchmark Script
set -e
echo 'Benchmarking omni-paypal...'
omni bench --module omni-paypal --iterations 10000
echo 'Benchmark complete.'
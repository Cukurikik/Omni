#!/bin/bash
# omni-razorpay - Benchmark Script
set -e
echo 'Benchmarking omni-razorpay...'
omni bench --module omni-razorpay --iterations 10000
echo 'Benchmark complete.'
#!/bin/bash
# omni-nodemailer-native - Benchmark Script
set -e
echo 'Benchmarking omni-nodemailer-native...'
omni bench --module omni-nodemailer-native --iterations 10000
echo 'Benchmark complete.'
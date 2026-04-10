#!/bin/bash
# omni-heroku-dynos - Benchmark Script
set -e
echo 'Benchmarking omni-heroku-dynos...'
omni bench --module omni-heroku-dynos --iterations 10000
echo 'Benchmark complete.'
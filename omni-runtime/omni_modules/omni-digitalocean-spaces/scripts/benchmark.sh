#!/bin/bash
# omni-digitalocean-spaces - Benchmark Script
set -e
echo 'Benchmarking omni-digitalocean-spaces...'
omni bench --module omni-digitalocean-spaces --iterations 10000
echo 'Benchmark complete.'
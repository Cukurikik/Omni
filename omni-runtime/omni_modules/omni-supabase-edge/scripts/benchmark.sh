#!/bin/bash
# omni-supabase-edge - Benchmark Script
set -e
echo 'Benchmarking omni-supabase-edge...'
omni bench --module omni-supabase-edge --iterations 10000
echo 'Benchmark complete.'
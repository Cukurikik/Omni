#!/bin/bash
# omni-supabase-storage - Benchmark Script
set -e
echo 'Benchmarking omni-supabase-storage...'
omni bench --module omni-supabase-storage --iterations 10000
echo 'Benchmark complete.'
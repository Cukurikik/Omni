#!/bin/bash
# omni-video-ffmpeg - Benchmark Script
set -e
echo 'Benchmarking omni-video-ffmpeg...'
omni bench --module omni-video-ffmpeg --iterations 10000
echo 'Benchmark complete.'
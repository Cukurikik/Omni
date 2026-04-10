#!/bin/bash
# omni-video-ffmpeg - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-video-ffmpeg healthy'
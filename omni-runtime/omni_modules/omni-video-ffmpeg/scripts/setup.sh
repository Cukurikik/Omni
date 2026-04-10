#!/bin/bash
# omni-video-ffmpeg - Setup Script
set -e
echo 'Setting up omni-video-ffmpeg...'
omni get omni-video-ffmpeg
omni build
echo 'omni-video-ffmpeg ready.'
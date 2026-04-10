#!/bin/bash
# omni-aliyun-oss - Setup Script
set -e
echo 'Setting up omni-aliyun-oss...'
omni get omni-aliyun-oss
omni build
echo 'omni-aliyun-oss ready.'
#!/bin/bash
# omni-wasabi-s3 - Setup Script
set -e
echo 'Setting up omni-wasabi-s3...'
omni get omni-wasabi-s3
omni build
echo 'omni-wasabi-s3 ready.'
#!/bin/bash
# omni-aws-s3 - Setup Script
set -e
echo 'Setting up omni-aws-s3...'
omni get omni-aws-s3
omni build
echo 'omni-aws-s3 ready.'
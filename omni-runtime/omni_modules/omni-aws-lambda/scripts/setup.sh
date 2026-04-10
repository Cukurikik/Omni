#!/bin/bash
# omni-aws-lambda - Setup Script
set -e
echo 'Setting up omni-aws-lambda...'
omni get omni-aws-lambda
omni build
echo 'omni-aws-lambda ready.'
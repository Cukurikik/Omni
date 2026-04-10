#!/bin/bash
# omni-apple-pay - Setup Script
set -e
echo 'Setting up omni-apple-pay...'
omni get omni-apple-pay
omni build
echo 'omni-apple-pay ready.'
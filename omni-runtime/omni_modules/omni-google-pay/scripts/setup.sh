#!/bin/bash
# omni-google-pay - Setup Script
set -e
echo 'Setting up omni-google-pay...'
omni get omni-google-pay
omni build
echo 'omni-google-pay ready.'
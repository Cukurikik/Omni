#!/bin/bash
# omni-lottie-web - Setup Script
set -e
echo 'Setting up omni-lottie-web...'
omni get omni-lottie-web
omni build
echo 'omni-lottie-web ready.'
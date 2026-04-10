#!/bin/bash
# omni-popmotion - Setup Script
set -e
echo 'Setting up omni-popmotion...'
omni get omni-popmotion
omni build
echo 'omni-popmotion ready.'
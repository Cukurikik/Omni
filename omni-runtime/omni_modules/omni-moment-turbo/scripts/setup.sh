#!/bin/bash
# omni-moment-turbo - Setup Script
set -e
echo 'Setting up omni-moment-turbo...'
omni get omni-moment-turbo
omni build
echo 'omni-moment-turbo ready.'
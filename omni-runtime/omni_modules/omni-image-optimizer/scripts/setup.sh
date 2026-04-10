#!/bin/bash
# omni-image-optimizer - Setup Script
set -e
echo 'Setting up omni-image-optimizer...'
omni get omni-image-optimizer
omni build
echo 'omni-image-optimizer ready.'
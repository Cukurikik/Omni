#!/bin/bash
# omni-canvas-turbo - Setup Script
set -e
echo 'Setting up omni-canvas-turbo...'
omni get omni-canvas-turbo
omni build
echo 'omni-canvas-turbo ready.'
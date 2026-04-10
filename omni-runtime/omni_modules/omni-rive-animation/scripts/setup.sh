#!/bin/bash
# omni-rive-animation - Setup Script
set -e
echo 'Setting up omni-rive-animation...'
omni get omni-rive-animation
omni build
echo 'omni-rive-animation ready.'
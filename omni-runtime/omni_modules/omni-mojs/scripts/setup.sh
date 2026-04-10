#!/bin/bash
# omni-mojs - Setup Script
set -e
echo 'Setting up omni-mojs...'
omni get omni-mojs
omni build
echo 'omni-mojs ready.'
#!/bin/bash
# omni-mongodb - Setup Script
set -e
echo 'Setting up omni-mongodb...'
omni get omni-mongodb
omni build
echo 'omni-mongodb ready.'
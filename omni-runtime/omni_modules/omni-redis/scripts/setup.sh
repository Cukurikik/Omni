#!/bin/bash
# omni-redis - Setup Script
set -e
echo 'Setting up omni-redis...'
omni get omni-redis
omni build
echo 'omni-redis ready.'
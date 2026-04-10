#!/bin/bash
# omni-sqlite-turbo - Setup Script
set -e
echo 'Setting up omni-sqlite-turbo...'
omni get omni-sqlite-turbo
omni build
echo 'omni-sqlite-turbo ready.'
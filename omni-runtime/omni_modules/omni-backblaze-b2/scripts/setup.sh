#!/bin/bash
# omni-backblaze-b2 - Setup Script
set -e
echo 'Setting up omni-backblaze-b2...'
omni get omni-backblaze-b2
omni build
echo 'omni-backblaze-b2 ready.'
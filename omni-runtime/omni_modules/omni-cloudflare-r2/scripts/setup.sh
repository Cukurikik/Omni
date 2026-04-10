#!/bin/bash
# omni-cloudflare-r2 - Setup Script
set -e
echo 'Setting up omni-cloudflare-r2...'
omni get omni-cloudflare-r2
omni build
echo 'omni-cloudflare-r2 ready.'
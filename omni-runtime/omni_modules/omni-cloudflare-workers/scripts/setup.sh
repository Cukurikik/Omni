#!/bin/bash
# omni-cloudflare-workers - Setup Script
set -e
echo 'Setting up omni-cloudflare-workers...'
omni get omni-cloudflare-workers
omni build
echo 'omni-cloudflare-workers ready.'
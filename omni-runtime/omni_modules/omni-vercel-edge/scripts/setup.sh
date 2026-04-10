#!/bin/bash
# omni-vercel-edge - Setup Script
set -e
echo 'Setting up omni-vercel-edge...'
omni get omni-vercel-edge
omni build
echo 'omni-vercel-edge ready.'
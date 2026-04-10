#!/bin/bash
# omni-netlify-edge - Setup Script
set -e
echo 'Setting up omni-netlify-edge...'
omni get omni-netlify-edge
omni build
echo 'omni-netlify-edge ready.'
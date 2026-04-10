#!/bin/bash
# omni-authorize-net - Setup Script
set -e
echo 'Setting up omni-authorize-net...'
omni get omni-authorize-net
omni build
echo 'omni-authorize-net ready.'
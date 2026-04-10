#!/bin/bash
# omni-scaleway-obj - Setup Script
set -e
echo 'Setting up omni-scaleway-obj...'
omni get omni-scaleway-obj
omni build
echo 'omni-scaleway-obj ready.'
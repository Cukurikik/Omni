#!/bin/bash
# omni-vultr-obj - Setup Script
set -e
echo 'Setting up omni-vultr-obj...'
omni get omni-vultr-obj
omni build
echo 'omni-vultr-obj ready.'
#!/bin/bash
# omni-stripe - Setup Script
set -e
echo 'Setting up omni-stripe...'
omni get omni-stripe
omni build
echo 'omni-stripe ready.'
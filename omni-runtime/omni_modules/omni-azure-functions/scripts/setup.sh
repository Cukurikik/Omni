#!/bin/bash
# omni-azure-functions - Setup Script
set -e
echo 'Setting up omni-azure-functions...'
omni get omni-azure-functions
omni build
echo 'omni-azure-functions ready.'
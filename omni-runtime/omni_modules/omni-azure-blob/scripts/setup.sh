#!/bin/bash
# omni-azure-blob - Setup Script
set -e
echo 'Setting up omni-azure-blob...'
omni get omni-azure-blob
omni build
echo 'omni-azure-blob ready.'
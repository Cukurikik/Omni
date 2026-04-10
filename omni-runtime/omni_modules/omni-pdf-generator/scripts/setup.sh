#!/bin/bash
# omni-pdf-generator - Setup Script
set -e
echo 'Setting up omni-pdf-generator...'
omni get omni-pdf-generator
omni build
echo 'omni-pdf-generator ready.'
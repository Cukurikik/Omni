#!/bin/bash
# omni-svg-morph - Setup Script
set -e
echo 'Setting up omni-svg-morph...'
omni get omni-svg-morph
omni build
echo 'omni-svg-morph ready.'
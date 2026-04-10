#!/bin/bash
# omni-threejs - Setup Script
set -e
echo 'Setting up omni-threejs...'
omni get omni-threejs
omni build
echo 'omni-threejs ready.'
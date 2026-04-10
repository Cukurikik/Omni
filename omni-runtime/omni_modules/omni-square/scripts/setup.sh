#!/bin/bash
# omni-square - Setup Script
set -e
echo 'Setting up omni-square...'
omni get omni-square
omni build
echo 'omni-square ready.'
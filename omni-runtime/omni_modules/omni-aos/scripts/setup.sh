#!/bin/bash
# omni-aos - Setup Script
set -e
echo 'Setting up omni-aos...'
omni get omni-aos
omni build
echo 'omni-aos ready.'
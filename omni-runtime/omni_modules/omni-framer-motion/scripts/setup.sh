#!/bin/bash
# omni-framer-motion - Setup Script
set -e
echo 'Setting up omni-framer-motion...'
omni get omni-framer-motion
omni build
echo 'omni-framer-motion ready.'
#!/bin/bash
# omni-velocity-js - Setup Script
set -e
echo 'Setting up omni-velocity-js...'
omni get omni-velocity-js
omni build
echo 'omni-velocity-js ready.'
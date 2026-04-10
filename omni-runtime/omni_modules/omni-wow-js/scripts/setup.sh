#!/bin/bash
# omni-wow-js - Setup Script
set -e
echo 'Setting up omni-wow-js...'
omni get omni-wow-js
omni build
echo 'omni-wow-js ready.'
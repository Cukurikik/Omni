#!/bin/bash
# omni-anime-js - Setup Script
set -e
echo 'Setting up omni-anime-js...'
omni get omni-anime-js
omni build
echo 'omni-anime-js ready.'
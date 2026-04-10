#!/bin/bash
# omni-matter-js - Setup Script
set -e
echo 'Setting up omni-matter-js...'
omni get omni-matter-js
omni build
echo 'omni-matter-js ready.'
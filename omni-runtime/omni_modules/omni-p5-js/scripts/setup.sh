#!/bin/bash
# omni-p5-js - Setup Script
set -e
echo 'Setting up omni-p5-js...'
omni get omni-p5-js
omni build
echo 'omni-p5-js ready.'
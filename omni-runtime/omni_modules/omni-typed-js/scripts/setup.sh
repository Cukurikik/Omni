#!/bin/bash
# omni-typed-js - Setup Script
set -e
echo 'Setting up omni-typed-js...'
omni get omni-typed-js
omni build
echo 'omni-typed-js ready.'
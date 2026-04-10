#!/bin/bash
# omni-webpack-killer - Setup Script
set -e
echo 'Setting up omni-webpack-killer...'
omni get omni-webpack-killer
omni build
echo 'omni-webpack-killer ready.'
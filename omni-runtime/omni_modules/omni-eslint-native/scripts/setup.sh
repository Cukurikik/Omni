#!/bin/bash
# omni-eslint-native - Setup Script
set -e
echo 'Setting up omni-eslint-native...'
omni get omni-eslint-native
omni build
echo 'omni-eslint-native ready.'
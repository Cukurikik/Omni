#!/bin/bash
# omni-prettier-native - Setup Script
set -e
echo 'Setting up omni-prettier-native...'
omni get omni-prettier-native
omni build
echo 'omni-prettier-native ready.'
#!/bin/bash
# omni-axios-native - Setup Script
set -e
echo 'Setting up omni-axios-native...'
omni get omni-axios-native
omni build
echo 'omni-axios-native ready.'